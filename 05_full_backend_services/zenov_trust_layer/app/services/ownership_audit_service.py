from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import asset_ownership_audit_logs, save_asset_ownership_audit_memory


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def record_ownership_event(
    *,
    asset_id: str,
    event_type: str,
    event_status: str,
    message: str,
    actor: str = "system",
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    log = {
        "ownership_audit_id": _new_id("OAUD"),
        "asset_id": asset_id,
        "event_type": event_type,
        "event_status": event_status,
        "actor": actor,
        "message": message,
        "snapshot": snapshot or {},
        "created_at": _now(),
    }
    save_asset_ownership_audit_memory(log)
    return log


def list_ownership_audit(asset_id: str | None = None) -> list[dict[str, Any]]:
    items = list(asset_ownership_audit_logs)
    if asset_id:
        items = [item for item in items if item.get("asset_id") == asset_id]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)
