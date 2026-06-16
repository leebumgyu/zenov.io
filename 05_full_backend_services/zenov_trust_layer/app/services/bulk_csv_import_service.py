from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Any, Optional
from uuid import uuid4

from ..crypto import canonical_json, sha256_hex
from ..services.report_service import generate_annual_report
from ..storage import (
    failed_import_rows,
    import_job_rows,
    import_jobs,
    taxi_daily_operations,
    save_failed_import_row_memory,
    save_import_job_memory,
    save_import_job_row_memory,
)
from .taxi_csv_import_service import FIELD_ALIASES, _float, _int, _operation_date, _pick, import_taxi_daily_csv


class BulkImportError(ValueError):
    pass


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _reason_code(error: str) -> str:
    if "REQUIRED_FIELD_MISSING:vehicle_id" in error:
        return "MISSING_VEHICLE_ID"
    if "REQUIRED_FIELD_MISSING" in error:
        return "MISSING_REQUIRED_FIELD"
    if "INVALID_DATE" in error:
        return "INVALID_DATE"
    if "INVALID_NUMBER" in error:
        return "INVALID_NUMBER"
    if "DUPLICATE_OPERATION" in error:
        return "DUPLICATE_OPERATION"
    if "OUTLIER_DISTANCE" in error:
        return "OUTLIER_DISTANCE"
    if "NEGATIVE" in error:
        return "NEGATIVE_DISTANCE"
    if "EVIDENCE" in error:
        return "EVIDENCE_CREATION_FAILED"
    if "MRV" in error:
        return "MRV_CALCULATION_FAILED"
    if "VERIFICATION" in error:
        return "VERIFICATION_REJECTED"
    return "ROW_PROCESSING_FAILED"


def _validate_row(row: dict[str, str]) -> dict[str, Any]:
    missing = [
        field
        for field in ("vehicle_id", "operation_date", "distance_km", "passenger_count", "daily_revenue", "driver_id")
        if _pick(row, field) is None
    ]
    if missing:
        raise ValueError(f"REQUIRED_FIELD_MISSING:{','.join(missing)}")
    vehicle_id = _pick(row, "vehicle_id")
    driver_id = _pick(row, "driver_id")
    operation_date = _operation_date(_pick(row, "operation_date"))
    distance_km = _float(_pick(row, "distance_km"), "distance_km")
    passenger_count = _int(_pick(row, "passenger_count"), "passenger_count")
    daily_revenue = _float(_pick(row, "daily_revenue"), "daily_revenue")
    provided_energy = _pick(row, "energy_consumed_kwh")
    energy_consumed_kwh = _float(provided_energy, "energy_consumed_kwh") if provided_energy is not None else None
    if distance_km <= 0:
        raise ValueError("NEGATIVE_DISTANCE")
    if distance_km > 1000:
        raise ValueError("OUTLIER_DISTANCE")
    if passenger_count < 0 or daily_revenue < 0 or (energy_consumed_kwh is not None and energy_consumed_kwh < 0):
        raise ValueError("NEGATIVE_DISTANCE")
    return {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "operation_date": operation_date,
        "distance_km": distance_km,
        "passenger_count": passenger_count,
        "daily_revenue": daily_revenue,
        "energy_consumed_kwh": energy_consumed_kwh,
    }


def _row_csv(row: dict[str, Any]) -> str:
    headers = ["vehicle_id", "operation_date", "distance_km", "passenger_count", "daily_revenue", "driver_id", "energy_consumed_kwh"]
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerow({key: "" if row.get(key) is None else row.get(key) for key in headers})
    return output.getvalue()


def _existing_operation_keys(company_id: str) -> set[tuple[str, str, str]]:
    return {
        (
            str(operation.get("company_id", "")),
            str(operation.get("vehicle_id")),
            str(operation.get("operation_date")),
        )
        for operation in taxi_daily_operations.values()
        if operation.get("company_id") == company_id and operation.get("vehicle_id") and operation.get("operation_date")
    }


def _save_failed(import_job_id: str, row_number: int, row: dict[str, str], reason: str) -> dict[str, Any]:
    failed = {
        "failed_row_id": _new_id("FROW"),
        "import_job_id": import_job_id,
        "row_number": row_number,
        "vehicle_id": _pick(row, "vehicle_id", ""),
        "reason_code": _reason_code(reason),
        "reason_message": reason,
        "raw_row": row,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_failed_import_row_memory(failed)
    return failed


def bulk_import_taxi_csv(
    *,
    csv_text: str,
    company_id: str = "ANSAN_TRANS",
    job_name: Optional[str] = None,
    source_filename: Optional[str] = None,
    baseline_type: str = "lpg_taxi",
    generate_report: bool = True,
    reporting_year: int = 2026,
) -> dict[str, Any]:
    reader = csv.DictReader(StringIO(csv_text.strip()))
    if not reader.fieldnames:
        raise BulkImportError("CSV_HEADER_MISSING")

    rows = list(reader)
    import_job_id = _new_id("JOB")
    seen_keys: set[tuple[str, str, str]] = set()
    existing_keys = _existing_operation_keys(company_id)
    job_rows: list[dict[str, Any]] = []
    failed_rows: list[dict[str, Any]] = []
    successes: list[dict[str, Any]] = []
    duplicate_count = 0

    job = {
        "import_job_id": import_job_id,
        "company_id": company_id,
        "job_name": job_name or "ansan-143-real-data-import",
        "source_filename": source_filename,
        "total_rows": len(rows),
        "success_count": 0,
        "failed_count": 0,
        "duplicate_count": 0,
        "evidence_count": 0,
        "mrv_count": 0,
        "verification_pass_count": 0,
        "asset_candidate_count": 0,
        "success_rate": 0,
        "report_id": None,
        "summary_hash": None,
        "status": "RUNNING",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    save_import_job_memory(job)

    for row_number, raw_row in enumerate(rows, start=1):
        row_id = _new_id("JROW")
        try:
            normalized = _validate_row(raw_row)
            key = (company_id, normalized["vehicle_id"], normalized["operation_date"])
            if key in seen_keys or key in existing_keys:
                duplicate_count += 1
                failure = _save_failed(import_job_id, row_number, raw_row, "DUPLICATE_OPERATION")
                job_row = {
                    "import_job_row_id": row_id,
                    "import_job_id": import_job_id,
                    "row_number": row_number,
                    "vehicle_id": normalized["vehicle_id"],
                    "operation_date": normalized["operation_date"],
                    "driver_id": normalized["driver_id"],
                    "row_status": "DUPLICATE",
                    "reason_code": failure["reason_code"],
                    "raw_row": raw_row,
                    "result_snapshot": failure,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                save_import_job_row_memory(job_row)
                job_rows.append(job_row)
                failed_rows.append(failure)
                continue
            seen_keys.add(key)

            result = import_taxi_daily_csv(
                csv_text=_row_csv(normalized),
                company_id=company_id,
                baseline_type=baseline_type,
                import_batch_name=f"{import_job_id}-row-{row_number}",
            )
            if result.get("failure_count"):
                failure = result["failures"][0]
                failure_record = _save_failed(import_job_id, row_number, raw_row, str(failure.get("reason", "ROW_PROCESSING_FAILED")))
                job_row = {
                    "import_job_row_id": row_id,
                    "import_job_id": import_job_id,
                    "row_number": row_number,
                    "vehicle_id": normalized["vehicle_id"],
                    "operation_date": normalized["operation_date"],
                    "driver_id": normalized["driver_id"],
                    "row_status": "FAILED",
                    "reason_code": failure_record["reason_code"],
                    "raw_row": raw_row,
                    "result_snapshot": failure,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                failed_rows.append(failure_record)
            else:
                success = result["successes"][0]
                successes.append(success)
                status = "SUCCESS" if success.get("verification_status") == "VERIFIED" and success.get("candidate_id") else "VERIFICATION_REJECTED"
                reason_code = None if status == "SUCCESS" else "VERIFICATION_REJECTED"
                if status != "SUCCESS":
                    failed_rows.append(_save_failed(import_job_id, row_number, raw_row, f"VERIFICATION_REJECTED:{success.get('verification_status')}"))
                job_row = {
                    "import_job_row_id": row_id,
                    "import_job_id": import_job_id,
                    "row_number": row_number,
                    "vehicle_id": normalized["vehicle_id"],
                    "operation_date": normalized["operation_date"],
                    "driver_id": normalized["driver_id"],
                    "row_status": status,
                    "reason_code": reason_code,
                    "packet_id": success.get("packet_id"),
                    "evidence_id": success.get("evidence_id"),
                    "mrv_id": success.get("mrv_id"),
                    "verification_id": success.get("verification_id"),
                    "asset_id": success.get("candidate_id"),
                    "raw_row": raw_row,
                    "result_snapshot": success,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            save_import_job_row_memory(job_row)
            job_rows.append(job_row)
        except ValueError as exc:
            failure = _save_failed(import_job_id, row_number, raw_row, str(exc))
            job_row = {
                "import_job_row_id": row_id,
                "import_job_id": import_job_id,
                "row_number": row_number,
                "vehicle_id": _pick(raw_row, "vehicle_id", ""),
                "operation_date": _pick(raw_row, "operation_date", ""),
                "driver_id": _pick(raw_row, "driver_id", ""),
                "row_status": "FAILED",
                "reason_code": failure["reason_code"],
                "raw_row": raw_row,
                "result_snapshot": failure,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            save_import_job_row_memory(job_row)
            job_rows.append(job_row)
            failed_rows.append(failure)

    report = None
    if generate_report and successes:
        report = generate_annual_report(
            project_name=f"{company_id} Taxi Carbon MRV Import Job",
            owner_entity=company_id,
            reporting_year=reporting_year,
        )

    success_count = sum(1 for row in job_rows if row.get("row_status") == "SUCCESS")
    failed_count = sum(1 for row in job_rows if row.get("row_status") in {"FAILED", "VERIFICATION_REJECTED"})
    evidence_count = sum(1 for row in job_rows if row.get("evidence_id"))
    mrv_count = sum(1 for row in job_rows if row.get("mrv_id"))
    verification_pass_count = sum(1 for row in job_rows if row.get("row_status") == "SUCCESS")
    asset_candidate_count = sum(1 for row in job_rows if row.get("asset_id"))
    summary_material = {
        "import_job_id": import_job_id,
        "total_rows": len(rows),
        "success_count": success_count,
        "failed_count": failed_count,
        "duplicate_count": duplicate_count,
        "evidence_count": evidence_count,
        "mrv_count": mrv_count,
        "verification_pass_count": verification_pass_count,
        "asset_candidate_count": asset_candidate_count,
        "report_id": report.get("report_id") if report else None,
    }
    job.update(
        {
            **summary_material,
            "success_rate": round((success_count / len(rows) * 100), 2) if rows else 0,
            "summary_hash": sha256_hex(canonical_json(summary_material)),
            "status": "COMPLETED",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_import_job_memory(job)
    return {
        **job,
        "rows": job_rows,
        "failed_rows": failed_rows,
        "report": report,
        "success_criteria": {
            "target_total_rows": 143,
            "actual_total_rows": len(rows),
            "chain": "CSV -> Packet -> Evidence -> MRV -> Verification -> Asset -> Registry -> Report",
        },
    }


def get_import_job(import_job_id: str) -> Optional[dict[str, Any]]:
    job = import_jobs.get(import_job_id)
    if not job:
        return None
    return {
        **job,
        "rows": [row for row in import_job_rows if row.get("import_job_id") == import_job_id],
        "failed_rows": [row for row in failed_import_rows if row.get("import_job_id") == import_job_id],
    }


def get_latest_import_job(company_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    jobs = list(import_jobs.values())
    if company_id:
        jobs = [job for job in jobs if job.get("company_id") == company_id]
    if not jobs:
        return None
    latest = sorted(jobs, key=lambda job: job.get("created_at", ""), reverse=True)[0]
    return get_import_job(latest["import_job_id"])
