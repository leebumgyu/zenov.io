from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import save_asset_ownership_memory, save_asset_transfer_memory
from .ownership_audit_service import record_ownership_event
from .ownership_service import OWNER_TYPES, ensure_asset_ownership, get_asset_ownership


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def transfer_asset(
    *,
    asset_id: str,
    to_owner_entity: str,
    to_owner_type: str,
    transfer_reason: str,
    actor: str = "system",
    transfer_reference: str | None = None,
) -> dict[str, Any]:
    if to_owner_type not in OWNER_TYPES:
        raise ValueError("OWNER_TYPE_NOT_SUPPORTED")
    if not to_owner_entity:
        raise ValueError("TO_OWNER_REQUIRED")
    current = get_asset_ownership(asset_id)
    ownership = current["ownership"]
    resolved_asset_id = ownership["asset_id"]
    pre_snapshot = {**ownership}
    transfer = {
        "transfer_id": _new_id("XFER"),
        "asset_id": resolved_asset_id,
        "from_owner_entity": ownership["owner_entity"],
        "from_owner_type": ownership["owner_type"],
        "to_owner_entity": to_owner_entity,
        "to_owner_type": to_owner_type,
        "transfer_reason": transfer_reason,
        "transfer_status": "COMPLETED",
        "transfer_reference": transfer_reference,
        "transferred_at": _now(),
        "actor": actor,
        "pre_transfer_snapshot": pre_snapshot,
        "post_transfer_snapshot": {},
    }
    ownership["owner_entity"] = to_owner_entity
    ownership["owner_type"] = to_owner_type
    ownership["updated_at"] = _now()
    transfer["post_transfer_snapshot"] = {**ownership}
    save_asset_ownership_memory(ownership)
    save_asset_transfer_memory(transfer)
    record_ownership_event(
        asset_id=resolved_asset_id,
        event_type="ASSET_TRANSFER_COMPLETED",
        event_status="COMPLETED",
        message=f"Asset ownership transferred from {transfer['from_owner_entity']} to {to_owner_entity}.",
        actor=actor,
        snapshot=transfer,
    )
    return {
        "status": "TRANSFER_COMPLETED",
        "asset_id": resolved_asset_id,
        "transfer": transfer,
        "ownership": ownership,
        "rule": "Transfer records ownership history only. It does not execute financial settlement or issue carbon credits.",
    }
