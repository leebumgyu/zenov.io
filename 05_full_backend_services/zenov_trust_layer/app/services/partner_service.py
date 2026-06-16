from __future__ import annotations

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..database.partner_crud import (
    get_partner,
    get_partner_health_logs,
    get_partner_integrations,
    get_partner_mappings,
    list_partners,
    save_health_log,
    save_partner,
    save_partner_integration,
    save_partner_mapping,
)
from ..storage import (
    carbon_asset_candidates,
    failed_import_rows,
    import_job_rows,
    import_jobs,
    mrv_verification_records,
    save_partner_health_memory,
)
from .partner_api_keys import create_partner_api_key
from .partner_mapping_engine import default_mapping_for, validate_mapping


PARTNER_HEALTH_MESSAGES = (
    "CONNECTED",
    "DATA RECEIVED",
    "MAPPING OK",
    "EVIDENCE CREATED",
    "MRV CALCULATED",
    "VERIFICATION PASSED",
    "ASSET GENERATED",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def register_partner(
    *,
    partner_name: str,
    partner_type: str = "TAXI_COMPANY",
    source_system: str = "TMONEY_CSV",
    data_format: str = "CSV",
    partner_id: str | None = None,
    field_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    partner_id = partner_id or f"PTR-KR-{partner_type.replace('_', '-')}-{uuid4().hex[:8].upper()}"
    template = default_mapping_for(source_system)
    mapping_field_map = field_map or template["field_map"]
    mapping_check = validate_mapping(template["standard_model"], mapping_field_map)
    partner = {
        "partner_id": partner_id,
        "partner_name": partner_name,
        "partner_type": partner_type,
        "source_system": source_system,
        "data_format": data_format,
        "lifecycle_status": "INVITED",
        "created_at": _now(),
        "updated_at": _now(),
    }
    mapping = {
        "mapping_id": _new_id("MAP"),
        "partner_id": partner_id,
        "source_type": source_system,
        "standard_model": template["standard_model"],
        "field_map": mapping_field_map,
        "mapping_status": mapping_check["status"],
        "mapping_check": mapping_check,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_partner(partner)
    save_partner_mapping(mapping)
    save_health_log(
        {
            "health_log_id": _new_id("PHL"),
            "partner_id": partner_id,
            "source_type": source_system,
            "event_type": "PARTNER_REGISTERED",
            "event_status": "INVITED",
            "message": "Partner registered with config-driven mapping.",
            "created_at": _now(),
        }
    )
    return {
        "status": "REGISTERED",
        "partner": partner,
        "mapping": mapping,
        "rule": "No code changes are required for a new partner when mapping config is complete.",
    }


def connect_partner(partner_id: str, integration_type: str = "CSV_IMPORT", endpoint_url: str | None = None) -> dict[str, Any]:
    partner = get_partner(partner_id)
    if not partner:
        raise ValueError(f"PARTNER_NOT_FOUND:{partner_id}")
    api_key = create_partner_api_key(partner_id)
    integration = {
        "integration_id": _new_id("INT"),
        "partner_id": partner_id,
        "integration_type": integration_type,
        "endpoint_url": endpoint_url,
        "status": "CONNECTED",
        "api_key_id": api_key["api_key_id"],
        "created_at": _now(),
        "last_health_check_at": _now(),
    }
    partner["lifecycle_status"] = "CONNECTED"
    partner["updated_at"] = _now()
    save_partner(partner)
    save_partner_integration(integration)
    save_health_log(
        {
            "health_log_id": _new_id("PHL"),
            "partner_id": partner_id,
            "source_type": partner.get("source_system"),
            "event_type": "PARTNER_CONNECTED",
            "event_status": "CONNECTED",
            "message": "Partner API key and integration created.",
            "created_at": _now(),
        }
    )
    return {
        "status": "CONNECTED",
        "partner": partner,
        "integration": integration,
        "api_key": api_key,
        "warning": "Store the raw api_key securely. It is returned only for onboarding demo.",
    }


def partner_status(partner_id: str | None = None) -> dict[str, Any]:
    if partner_id:
        partner = get_partner(partner_id)
        if not partner:
            return {"status": "NOT_FOUND", "partner_id": partner_id}
        return {
            "status": partner.get("lifecycle_status"),
            "partner": partner,
            "mappings": get_partner_mappings(partner_id),
            "integrations": get_partner_integrations(partner_id),
            "health_logs": get_partner_health_logs(partner_id)[-20:],
        }
    partners = list_partners()
    counts = Counter(partner.get("lifecycle_status", "UNKNOWN") for partner in partners)
    return {
        "status": "OK",
        "partner_count": len(partners),
        "lifecycle_counts": dict(counts),
        "partners": partners,
    }


def _jobs(partner_id: str) -> list[dict[str, Any]]:
    return [job for job in import_jobs.values() if str(job.get("company_id")) == partner_id]


def _rows(partner_id: str) -> list[dict[str, Any]]:
    job_ids = {job["import_job_id"] for job in _jobs(partner_id)}
    return [row for row in import_job_rows if row.get("import_job_id") in job_ids]


def _failed_rows(partner_id: str) -> list[dict[str, Any]]:
    job_ids = {job["import_job_id"] for job in _jobs(partner_id)}
    return [row for row in failed_import_rows if row.get("import_job_id") in job_ids]


def _latest_time(items: list[dict[str, Any]], keys: tuple[str, ...] = ("completed_at", "created_at")) -> str | None:
    values = []
    for item in items:
        for key in keys:
            if item.get(key):
                values.append(str(item[key]))
                break
    return max(values) if values else None


def partner_health(partner_id: str) -> dict[str, Any]:
    jobs = _jobs(partner_id)
    rows = _rows(partner_id)
    failed = _failed_rows(partner_id)
    integrations = get_partner_integrations(partner_id)
    health_logs = get_partner_health_logs(partner_id)
    mapping_errors = [row for row in failed if row.get("reason_code") in {"MISSING_VEHICLE_ID", "MISSING_REQUIRED_FIELD", "INVALID_DATE", "INVALID_NUMBER"}]
    verification_rows = [
        mrv_verification_records[row["verification_id"]]
        for row in rows
        if row.get("verification_id") in mrv_verification_records
    ]
    pass_count = sum(1 for item in verification_rows if item.get("verification_status") == "VERIFIED")
    api_status = "CONNECTED" if jobs or integrations else "WAITING_FOR_DATA"
    last_data_received = _latest_time(jobs) or _latest_time(health_logs)
    health = {
        "partner_id": partner_id,
        "api_status": api_status,
        "last_data_received_at": last_data_received,
        "upload_success_count": sum(1 for row in rows if row.get("row_status") == "SUCCESS"),
        "upload_failed_count": sum(1 for row in rows if row.get("row_status") in {"FAILED", "VERIFICATION_REJECTED"}),
        "duplicate_count": sum(1 for row in rows if row.get("row_status") == "DUPLICATE"),
        "mapping_error_count": len(mapping_errors),
        "evidence_count": sum(1 for row in rows if row.get("evidence_id")),
        "mrv_count": sum(1 for row in rows if row.get("mrv_id")),
        "verification_pass_rate": round((pass_count / len(verification_rows) * 100), 2) if verification_rows else 0,
        "asset_generated_count": sum(1 for row in rows if row.get("asset_id")),
        "status_messages": list(PARTNER_HEALTH_MESSAGES),
        "generated_at": _now(),
    }
    save_partner_health_memory(health)
    return health


def partner_dashboard(partner_id: str) -> dict[str, Any]:
    health = partner_health(partner_id)
    assets = [
        item for item in carbon_asset_candidates.values()
        if str(item.get("owner_entity")) == partner_id
    ]
    return {
        "partner_id": partner_id,
        "health": health,
        "asset_summary": {
            "asset_count": len(assets),
            "total_reduction_tco2e": round(sum(float(item.get("issued_quantity_tco2e", 0) or 0) for item in assets), 6),
            "estimated_value_krw": round(sum(float(item.get("estimated_value_krw", 0) or 0) for item in assets), 2),
            "registry_ready_count": sum(1 for item in assets if item.get("candidate_status") in {"CANDIDATE", "UNDER_REVIEW", "ELIGIBLE_FOR_REGISTRY"}),
        },
        "latest_import": _jobs(partner_id)[-1] if _jobs(partner_id) else None,
        "operator_savings_message": "Partner dashboard is an operating-cost reduction tool, not a cosmetic screen.",
    }


def partner_imports(partner_id: str) -> dict[str, Any]:
    jobs = _jobs(partner_id)
    return {
        "partner_id": partner_id,
        "count": len(jobs),
        "jobs": jobs,
    }


def partner_mapping_errors(partner_id: str) -> dict[str, Any]:
    failed = _failed_rows(partner_id)
    mapping_errors = [
        row for row in failed
        if row.get("reason_code") in {"MISSING_VEHICLE_ID", "MISSING_REQUIRED_FIELD", "INVALID_DATE", "INVALID_NUMBER", "NEGATIVE_DISTANCE"}
    ]
    counts = Counter(row.get("reason_code", "UNKNOWN") for row in mapping_errors)
    return {
        "partner_id": partner_id,
        "mapping_error_count": len(mapping_errors),
        "reason_counts": [{"reason_code": reason, "count": count} for reason, count in counts.most_common()],
        "items": mapping_errors[:100],
    }
