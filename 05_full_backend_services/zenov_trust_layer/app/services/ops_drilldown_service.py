from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..database.crud import get_full_trace_detail
from ..storage import (
    dead_letter_queue,
    failed_import_rows,
    import_job_rows,
    import_jobs,
    save_dead_letter_memory,
)


RETRYABLE_STATUSES = {"FAILED", "DUPLICATE", "VERIFICATION_REJECTED", "RETRY_PENDING", "RETRYING"}
MAX_RETRY_COUNT = 3


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _status_for_step(value: Optional[str], failed: bool = False) -> str:
    if failed:
        return "FAILED"
    return "OK" if value else "MISSING"


def _job_rows(job_id: str) -> list[dict[str, Any]]:
    return [row for row in import_job_rows if row.get("import_job_id") == job_id]


def _job_failed_rows(job_id: str) -> list[dict[str, Any]]:
    return [row for row in failed_import_rows if row.get("import_job_id") == job_id]


def _find_row_by_packet(packet_id: str) -> Optional[dict[str, Any]]:
    return next((row for row in import_job_rows if row.get("packet_id") == packet_id), None)


def _find_row_by_evidence(evidence_id: str) -> Optional[dict[str, Any]]:
    return next((row for row in import_job_rows if row.get("evidence_id") == evidence_id), None)


def _find_row_by_job_row_id(row_id: str) -> Optional[dict[str, Any]]:
    return next((row for row in import_job_rows if row.get("import_job_row_id") == row_id), None)


def drilldown_by_packet(packet_id: str) -> dict[str, Any]:
    trace = get_full_trace_detail(packet_id)
    row = _find_row_by_packet(packet_id)
    failed = bool(trace.get("reject_log")) or (row or {}).get("row_status") in {"FAILED", "DUPLICATE", "VERIFICATION_REJECTED"}
    reason_code = (row or {}).get("reason_code")
    if not reason_code and trace.get("reject_log"):
        first_reject = trace["reject_log"][0]
        reasons = first_reject.get("reason") or []
        reason_code = str(reasons[0]).split(":", 1)[0] if reasons else first_reject.get("reason_code")
    chain = {
        "packet_id": packet_id,
        "evidence_id": trace.get("evidence_id"),
        "mrv_id": trace.get("mrv_id"),
        "verification_id": trace.get("verification_id"),
        "asset_id": trace.get("asset_id"),
        "registry_id": trace.get("registry_id"),
    }
    stages = [
        {"stage": "PACKET", "id": chain["packet_id"], "status": _status_for_step(chain["packet_id"])},
        {"stage": "EVIDENCE", "id": chain["evidence_id"], "status": _status_for_step(chain["evidence_id"], failed and not chain["evidence_id"])},
        {"stage": "MRV", "id": chain["mrv_id"], "status": _status_for_step(chain["mrv_id"], failed and not chain["mrv_id"])},
        {"stage": "VERIFICATION", "id": chain["verification_id"], "status": _status_for_step(chain["verification_id"], failed and not chain["verification_id"])},
        {"stage": "ASSET", "id": chain["asset_id"], "status": _status_for_step(chain["asset_id"], failed and not chain["asset_id"])},
        {"stage": "REGISTRY", "id": chain["registry_id"], "status": (trace.get("registry") or {}).get("registry_status", "NOT_REGISTERED")},
    ]
    return {
        "lookup_type": "packet",
        "lookup_id": packet_id,
        "chain": chain,
        "stages": stages,
        "reason_code": reason_code,
        "error_message": (row or {}).get("result_snapshot", {}).get("reason_message") or (row or {}).get("result_snapshot", {}).get("reason"),
        "retry_status": (row or {}).get("retry_status", "NOT_REQUIRED" if not failed else "FAILED"),
        "retry_count": (row or {}).get("retry_count", 0),
        "traceability_status": trace.get("traceability_status"),
        "trace": trace,
    }


def drilldown_by_evidence(evidence_id: str) -> dict[str, Any]:
    row = _find_row_by_evidence(evidence_id)
    if not row:
        return {
            "lookup_type": "evidence",
            "lookup_id": evidence_id,
            "traceability_status": "BROKEN",
            "reason_code": "EVIDENCE_NOT_FOUND",
            "stages": [{"stage": "EVIDENCE", "id": evidence_id, "status": "MISSING"}],
        }
    result = drilldown_by_packet(row["packet_id"])
    result["lookup_type"] = "evidence"
    result["lookup_id"] = evidence_id
    return result


def drilldown_by_job(job_id: str) -> dict[str, Any]:
    job = import_jobs.get(job_id)
    rows = _job_rows(job_id)
    failed_rows = _job_failed_rows(job_id)
    reason_counts = Counter(row.get("reason_code") for row in rows if row.get("reason_code"))
    first_success = next((row for row in rows if row.get("packet_id")), None)
    return {
        "lookup_type": "job",
        "lookup_id": job_id,
        "job": job,
        "row_count": len(rows),
        "failed_row_count": len(failed_rows),
        "top_reason_codes": [
            {"reason_code": reason, "count": count}
            for reason, count in reason_counts.most_common(10)
            if reason
        ],
        "sample_chain": drilldown_by_packet(first_success["packet_id"])["chain"] if first_success else None,
        "rows": rows[:50],
        "failed_rows": failed_rows[:50],
        "traceability_status": "JOB_COMPLETE" if job else "BROKEN",
    }


def drilldown(lookup_id: str) -> dict[str, Any]:
    if lookup_id in import_jobs:
        return drilldown_by_job(lookup_id)
    if _find_row_by_evidence(lookup_id):
        return drilldown_by_evidence(lookup_id)
    row = _find_row_by_job_row_id(lookup_id)
    if row and row.get("packet_id"):
        result = drilldown_by_packet(row["packet_id"])
        result["lookup_type"] = "import_job_row"
        result["lookup_id"] = lookup_id
        return result
    return drilldown_by_packet(lookup_id)


def root_cause_summary() -> dict[str, Any]:
    rows_with_reasons = [row for row in import_job_rows if row.get("reason_code")]
    failed_reason_counts = Counter(row["reason_code"] for row in rows_with_reasons)
    retry_counts = Counter(row.get("retry_status", row.get("row_status", "UNKNOWN")) for row in rows_with_reasons)
    latest_failed = sorted(rows_with_reasons, key=lambda row: row.get("created_at", ""), reverse=True)[:20]
    return {
        "generated_at": _now(),
        "failed_rows": len(rows_with_reasons),
        "top_10_reason_codes": [
            {"reason_code": reason, "count": count}
            for reason, count in failed_reason_counts.most_common(10)
        ],
        "retry_status_counts": dict(retry_counts),
        "dead_letter_count": len(dead_letter_queue),
        "latest_failed_rows": latest_failed,
        "operator_message": "Monitoring is not a status screen. It must identify what failed and why within 30 seconds.",
    }


def retry_failed_row(row_id: str) -> dict[str, Any]:
    row = _find_row_by_job_row_id(row_id)
    if not row:
        return {"status": "NOT_FOUND", "reason_code": "IMPORT_ROW_NOT_FOUND", "row_id": row_id}
    if row.get("row_status") not in RETRYABLE_STATUSES:
        return {"status": "NOT_RETRYABLE", "row_id": row_id, "row_status": row.get("row_status")}
    retry_count = int(row.get("retry_count", 0)) + 1
    row["retry_count"] = retry_count
    row["retry_status"] = "RETRYING"
    row["last_retry_at"] = _now()
    if retry_count > MAX_RETRY_COUNT:
        row["retry_status"] = "DLQ"
        dlq_item = {
            "dlq_id": _new_id("DLQ"),
            "import_job_row_id": row_id,
            "import_job_id": row.get("import_job_id"),
            "vehicle_id": row.get("vehicle_id"),
            "reason_code": row.get("reason_code", "RETRY_LIMIT_EXCEEDED"),
            "retry_count": retry_count,
            "raw_row": row.get("raw_row"),
            "created_at": _now(),
            "status": "MANUAL_REVIEW_REQUIRED",
        }
        save_dead_letter_memory(dlq_item)
        return {"status": "DLQ", "row": row, "dead_letter": dlq_item}
    row["retry_status"] = "RETRY_PENDING"
    return {"status": "RETRY_PENDING", "row": row}
