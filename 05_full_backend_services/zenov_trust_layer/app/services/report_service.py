from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..crypto import canonical_json, sha256_hex
from ..database.report_crud import get_report, list_reports, save_report
from .methodology_service import create_methodology_snapshot, get_registered_methodology, register_methodology_from_config
from ..storage import (
    carbon_asset_candidates,
    digital_evidence,
    integrity_reports,
    mrv_verification_records,
    taxi_daily_operations,
    taxi_mrv_results,
    trust_packets,
)


REPORT_ENGINE_VERSION = "ZENOV_ANNUAL_MRV_REPORT_ENGINE_V1.0"
REPORT_LEGAL_NOTICE = (
    "This Annual Carbon MRV Report is a generated MRV evidence package. "
    "It is not a carbon credit issuance, registry approval, financial approval, "
    "or certification decision. External verification and applicable legal review are required."
)


def _new_report_id() -> str:
    return f"RPT-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _period_for_year(reporting_year: int) -> tuple[str, str]:
    return f"{reporting_year}-01-01", f"{reporting_year}-12-31"


def _operation_date(operation: dict[str, Any]) -> str:
    return str(operation.get("operation_date", ""))


def _filter_operations(owner_entity: str, reporting_year: int) -> list[dict[str, Any]]:
    year_prefix = f"{reporting_year}-"
    operations = [
        operation
        for operation in taxi_daily_operations.values()
        if _operation_date(operation).startswith(year_prefix)
    ]
    if not owner_entity:
        return operations

    owner_packet_ids = {
        candidate["packet_id"]
        for candidate in carbon_asset_candidates.values()
        if candidate.get("owner_entity") == owner_entity
    }
    if owner_packet_ids:
        return [operation for operation in operations if operation.get("packet_id") in owner_packet_ids]
    return operations


def _linked_items(operations: list[dict[str, Any]]) -> dict[str, Any]:
    packet_ids = {operation["packet_id"] for operation in operations if operation.get("packet_id")}
    mrv_ids = {operation["mrv_id"] for operation in operations if operation.get("mrv_id")}
    evidence_ids = {operation["evidence_id"] for operation in operations if operation.get("evidence_id")}
    verification_ids = {
        operation["verification_id"]
        for operation in operations
        if operation.get("verification_id")
    }
    candidates = [
        candidate
        for candidate in carbon_asset_candidates.values()
        if candidate.get("packet_id") in packet_ids or candidate.get("mrv_id") in mrv_ids
    ]
    verifications = [
        verification
        for verification in mrv_verification_records.values()
        if verification.get("verification_id") in verification_ids
    ]
    evidences = [
        evidence
        for evidence in digital_evidence.values()
        if evidence.get("evidence_id") in evidence_ids or evidence.get("packet_id") in packet_ids
    ]
    integrity = [
        report
        for report in integrity_reports.values()
        if report.get("evidence_id") in {evidence.get("evidence_id") for evidence in evidences}
    ]
    packets = [
        packet.model_dump() if hasattr(packet, "model_dump") else packet
        for packet_id, packet in trust_packets.items()
        if packet_id in packet_ids
    ]
    mrvs = [
        mrv
        for mrv in taxi_mrv_results.values()
        if mrv.get("mrv_id") in mrv_ids or mrv.get("packet_id") in packet_ids
    ]
    return {
        "packet_ids": packet_ids,
        "mrv_ids": mrv_ids,
        "evidence_ids": evidence_ids,
        "packets": packets,
        "mrvs": mrvs,
        "evidences": evidences,
        "integrity_reports": integrity,
        "verifications": verifications,
        "candidates": candidates,
    }


def _verification_summary(verifications: list[dict[str, Any]]) -> dict[str, Any]:
    if not verifications:
        return {
            "verification_score": 0,
            "verification_status": "PENDING",
            "status_counts": {},
        }
    score = sum(float(item.get("verification_score", 0) or 0) for item in verifications) / len(verifications)
    counts = Counter(str(item.get("verification_status", "PENDING")) for item in verifications)
    if counts.get("REJECTED"):
        status = "REJECTED"
    elif counts.get("CONDITIONALLY_VERIFIED"):
        status = "CONDITIONALLY_VERIFIED"
    elif counts.get("VERIFIED") == len(verifications):
        status = "VERIFIED"
    else:
        status = "UNDER_REVIEW"
    return {
        "verification_score": round(score, 2),
        "verification_status": status,
        "status_counts": dict(counts),
    }


def generate_annual_report(
    *,
    project_name: str,
    owner_entity: str,
    reporting_year: int,
    methodology_id: Optional[str] = None,
    methodology_version: Optional[str] = None,
    language_code: str = "ko-KR",
) -> dict[str, Any]:
    operations = _filter_operations(owner_entity, reporting_year)
    linked = _linked_items(operations)
    mrvs = linked["mrvs"]
    candidates = linked["candidates"]
    evidences = linked["evidences"]
    integrity = linked["integrity_reports"]
    verifications = linked["verifications"]
    period_start, period_end = _period_for_year(reporting_year)

    vehicle_ids = {operation.get("vehicle_id") for operation in operations if operation.get("vehicle_id")}
    operation_days = {
        (operation.get("vehicle_id"), operation.get("operation_date"))
        for operation in operations
        if operation.get("vehicle_id") and operation.get("operation_date")
    }
    baseline = sum(float(mrv.get("baseline_co2e_kg", 0) or 0) for mrv in mrvs)
    project = sum(float(mrv.get("ev_co2e_kg", 0) or 0) for mrv in mrvs)
    reduction = sum(float(mrv.get("reduction_co2e_kg", 0) or 0) for mrv in mrvs)
    estimated_value_krw = sum(float(candidate.get("estimated_value_krw", 0) or 0) for candidate in candidates)
    estimated_value_usd = sum(float(candidate.get("estimated_value_usd", 0) or 0) for candidate in candidates)
    verification = _verification_summary(verifications)

    if not methodology_id and mrvs:
        methodology_id = str(mrvs[0].get("methodology_id", "UNKNOWN"))
    if not methodology_version and mrvs:
        methodology_version = str(mrvs[0].get("methodology_version", "UNKNOWN"))

    registry_snapshot = {
        "asset_candidate_count": len(candidates),
        "candidate_quantity_tco2e": sum(float(candidate.get("issued_quantity_tco2e", 0) or 0) for candidate in candidates),
        "registry_status_counts": dict(Counter(candidate.get("registry_status", "NOT_REGISTERED") for candidate in candidates)),
        "assets": [
            {
                "asset_id": candidate.get("candidate_id"),
                "serial_number": candidate.get("serial_number"),
                "registry_id": candidate.get("registry_id"),
                "registry_status": candidate.get("registry_status"),
                "issued_quantity_tco2e": candidate.get("issued_quantity_tco2e"),
                "estimated_value_krw": candidate.get("estimated_value_krw"),
                "owner_entity": candidate.get("owner_entity"),
            }
            for candidate in candidates
        ],
    }
    registry_status_counts = registry_snapshot["registry_status_counts"]
    if registry_status_counts.get("REGISTERED") == len(candidates) and candidates:
        asset_status = "REGISTERED"
    elif candidates:
        asset_status = "CANDIDATE"
    else:
        asset_status = "NO_ASSET_CANDIDATE"

    report_id = _new_report_id()
    created_at = datetime.now(timezone.utc).isoformat()
    snapshot = {
        "report_engine_version": REPORT_ENGINE_VERSION,
        "legal_notice": REPORT_LEGAL_NOTICE,
        "carbon_trust_certificate": {
            "title": "ZENOV CARBON TRUST VERIFIED",
            "report_id": report_id,
            "methodology": methodology_id,
            "methodology_version": methodology_version,
            "verification_score": verification["verification_score"],
            "verification_status": verification["verification_status"],
            "asset_status": asset_status,
            "generated_at": created_at,
            "report_hash": None,
        },
        "project_overview": {
            "project_name": project_name,
            "owner_entity": owner_entity,
            "report_period_start": period_start,
            "report_period_end": period_end,
            "methodology_id": methodology_id,
            "methodology_version": methodology_version,
            "language_code": language_code,
        },
        "data_summary": {
            "vehicle_count": len(vehicle_ids),
            "total_distance_km": sum(float(operation.get("distance_km", 0) or 0) for operation in operations),
            "total_revenue": sum(float(operation.get("daily_revenue", 0) or 0) for operation in operations),
            "operation_day_count": len(operation_days),
        },
        "carbon_mrv_result": {
            "baseline_emission_kgco2e": baseline,
            "project_emission_kgco2e": project,
            "reduction_kgco2e": reduction,
            "reduction_tco2e": reduction / 1000,
        },
        "verification_result": verification | {
            "methodology_id": methodology_id,
            "methodology_version": methodology_version,
        },
        "carbon_asset_summary": registry_snapshot,
        "evidence_summary": {
            "packet_count": len(linked["packet_ids"]),
            "evidence_count": len(evidences),
            "hash_verified_count": sum(1 for item in integrity if item.get("hash_verified")),
            "signature_verified_count": sum(1 for item in integrity if item.get("signature_verified")),
            "canonical_verified_count": sum(1 for item in integrity if item.get("canonical_verified")),
        },
    }

    report_hash = sha256_hex(canonical_json(snapshot))
    snapshot["carbon_trust_certificate"]["report_hash"] = report_hash
    methodology_record = None
    if methodology_id and methodology_version:
        methodology_record = get_registered_methodology(methodology_id, methodology_version)
    if not methodology_record:
        methodology_record = register_methodology_from_config()
    methodology_snapshot = create_methodology_snapshot(
        methodology_id=str(methodology_id or methodology_record.get("methodology_id")),
        methodology_version=str(methodology_version or methodology_record.get("version")),
        linked_type="REPORT",
        linked_id=report_id,
        payload={
            "report_hash": report_hash,
            "report_period_start": period_start,
            "report_period_end": period_end,
            "methodology_record": methodology_record,
        },
    )
    report = {
        "report_id": report_id,
        "project_name": project_name,
        "owner_entity": owner_entity,
        "report_period_start": period_start,
        "report_period_end": period_end,
        "methodology_id": methodology_id,
        "methodology_version": methodology_version,
        "language_code": language_code,
        "packet_count": snapshot["evidence_summary"]["packet_count"],
        "evidence_count": snapshot["evidence_summary"]["evidence_count"],
        "mrv_count": len(mrvs),
        "asset_candidate_count": len(candidates),
        "total_distance_km": snapshot["data_summary"]["total_distance_km"],
        "total_revenue": snapshot["data_summary"]["total_revenue"],
        "baseline_emission_kgco2e": baseline,
        "project_emission_kgco2e": project,
        "reduction_kgco2e": reduction,
        "reduction_tco2e": reduction / 1000,
        "estimated_value_krw": estimated_value_krw,
        "estimated_value_usd": round(estimated_value_usd, 2),
        "verification_score": verification["verification_score"],
        "verification_status": verification["verification_status"],
        "registry_snapshot": registry_snapshot,
        "methodology_snapshot": methodology_snapshot,
        "report_snapshot": snapshot,
        "report_hash": report_hash,
        "status": "GENERATED",
        "created_at": created_at,
    }
    save_report(report)
    return report


def get_mrv_report(report_id: str) -> Optional[dict[str, Any]]:
    return get_report(report_id)


def list_mrv_reports() -> list[dict[str, Any]]:
    return list_reports()
