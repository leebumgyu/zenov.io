from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import (
    import_job_rows,
    import_jobs,
    mrv_reports,
    mrv_verification_records,
    save_sla_snapshot_memory,
    sla_snapshots,
    taxi_mrv_results,
    trust_packets,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def calculate_sla_snapshot(tenant_id: Optional[str] = "ansan-trans") -> dict[str, Any]:
    total_rows = len(import_job_rows)
    successful_rows = sum(1 for row in import_job_rows if row.get("row_status") in {"SUCCESS", "VERIFIED"})
    verified = sum(1 for item in mrv_verification_records.values() if item.get("verification_status") == "VERIFIED")
    total_verifications = len(mrv_verification_records)
    packets = len(trust_packets)
    mrv_count = len(taxi_mrv_results)
    reports = len(mrv_reports)

    data_collection_success_rate = round((packets / max(packets, 1)) * 100, 2) if packets else 0
    import_success_rate = round((successful_rows / total_rows) * 100, 2) if total_rows else 0
    verification_success_rate = round((verified / total_verifications) * 100, 2) if total_verifications else 0
    api_response_time_ms = 120.0
    sla_status = "GREEN"
    if import_success_rate and import_success_rate < 95:
        sla_status = "YELLOW"
    if verification_success_rate and verification_success_rate < 80:
        sla_status = "RED"
    snapshot = {
        "sla_snapshot_id": _new_id("SLA"),
        "tenant_id": tenant_id,
        "data_collection_success_rate": data_collection_success_rate,
        "api_response_time_ms": api_response_time_ms,
        "import_success_rate": import_success_rate,
        "verification_success_rate": verification_success_rate,
        "sla_status": sla_status,
        "snapshot": {
            "packet_count": packets,
            "mrv_count": mrv_count,
            "report_count": reports,
            "import_job_count": len(import_jobs),
            "import_row_count": total_rows,
            "successful_import_rows": successful_rows,
            "verification_count": total_verifications,
            "verified_count": verified,
        },
        "created_at": _now(),
    }
    save_sla_snapshot_memory(snapshot)
    return snapshot


def latest_sla_snapshot(tenant_id: Optional[str] = "ansan-trans") -> dict[str, Any]:
    items = [
        item for item in sla_snapshots.values()
        if item.get("tenant_id") == tenant_id
    ]
    if not items:
        return calculate_sla_snapshot(tenant_id)
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)[0]
