from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..database.partner_crud import save_health_log
from .partner_mapping_engine import map_external_record


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ingest_partner_payload(partner_id: str, source_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    mapped = map_external_record(partner_id, source_type, payload)
    log = {
        "health_log_id": f"PHL-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
        "partner_id": partner_id,
        "source_type": source_type,
        "event_type": "DATA_RECEIVED",
        "event_status": mapped["mapping_status"],
        "message": "Partner payload normalized into Zenov standard model.",
        "mapping_errors": mapped["mapping_errors"],
        "created_at": _now(),
    }
    save_health_log(log)
    return {
        "status": "ACCEPTED" if mapped["mapping_status"] == "MAPPING_OK" else "MAPPING_FAILED",
        "partner_id": partner_id,
        "source_type": source_type,
        "mapped": mapped,
        "health_log": log,
        "next_step": "Evidence Layer" if mapped["mapping_status"] == "MAPPING_OK" else "Fix partner_data_mapping config",
    }
