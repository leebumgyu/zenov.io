from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import asset_custody_records, save_asset_custody_memory
from .ownership_audit_service import record_ownership_event


DEFAULT_CUSTODIAN_ENTITY = "ZENOV_CUSTODY"
DEFAULT_CUSTODIAN_TYPE = "Zenov Asset Pool"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def ensure_custody(
    asset_id: str,
    *,
    custodian_entity: str = DEFAULT_CUSTODIAN_ENTITY,
    custodian_type: str = DEFAULT_CUSTODIAN_TYPE,
    custody_scope: str = "REGISTRY_PREPARATION",
) -> dict[str, Any]:
    existing = asset_custody_records.get(asset_id)
    if existing:
        return existing
    record = {
        "custody_id": _new_id("CUST"),
        "asset_id": asset_id,
        "custodian_entity": custodian_entity,
        "custodian_type": custodian_type,
        "custody_scope": custody_scope,
        "custody_status": "HELD",
        "started_at": _now(),
        "ended_at": None,
        "custody_terms": {
            "simulation_only": True,
            "note": "Custody is separated from beneficial ownership for Registry preparation.",
        },
    }
    save_asset_custody_memory(record)
    record_ownership_event(
        asset_id=asset_id,
        event_type="CUSTODY_REGISTERED",
        event_status="HELD",
        message="Asset custody record registered.",
        snapshot=record,
    )
    return record
