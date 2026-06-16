from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import (
    save_settlement_ledger_entry_memory,
    save_settlement_record_memory,
    settlement_ledger_entries,
    settlement_records,
)


ALLOWED_SETTLEMENT_STATUSES = {"PENDING", "APPROVED", "SETTLED", "REVERSED", "CANCELLED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def append_settlement_ledger(
    *,
    settlement_id: str,
    event_type: str,
    event_status: str,
    message: str,
    actor: str = "system",
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = {
        "ledger_entry_id": _new_id("SLEDGER"),
        "settlement_id": settlement_id,
        "event_type": event_type,
        "event_status": event_status,
        "message": message,
        "actor": actor,
        "snapshot": snapshot or {},
        "created_at": _now(),
    }
    save_settlement_ledger_entry_memory(entry)
    return entry


def save_settlement_record(record: dict[str, Any]) -> dict[str, Any]:
    save_settlement_record_memory(record)
    append_settlement_ledger(
        settlement_id=record["settlement_id"],
        event_type="SETTLEMENT_RECORD_CREATED",
        event_status=record.get("status", "PENDING"),
        message="Settlement simulation ledger record created.",
        snapshot=record,
    )
    return record


def update_settlement_status(settlement_id: str, status: str, actor: str = "system") -> dict[str, Any]:
    new_status = status.upper()
    if new_status not in ALLOWED_SETTLEMENT_STATUSES:
        raise ValueError("SETTLEMENT_STATUS_NOT_SUPPORTED")
    record = settlement_records.get(settlement_id)
    if not record:
        raise ValueError("SETTLEMENT_NOT_FOUND")
    record["status"] = new_status
    stamp_key = {
        "APPROVED": "approved_at",
        "SETTLED": "settled_at",
        "REVERSED": "reversed_at",
        "CANCELLED": "cancelled_at",
    }.get(new_status)
    if stamp_key:
        record[stamp_key] = _now()
    save_settlement_record_memory(record)
    append_settlement_ledger(
        settlement_id=settlement_id,
        event_type=f"SETTLEMENT_{new_status}",
        event_status=new_status,
        message=f"Settlement status changed to {new_status}.",
        actor=actor,
        snapshot=record,
    )
    return record


def get_settlement_record(settlement_id: str) -> dict[str, Any] | None:
    return settlement_records.get(settlement_id)


def list_settlement_records(tenant_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    items = list(settlement_records.values())
    if tenant_id:
        items = [item for item in items if str(item.get("tenant_id")) == tenant_id]
    if status:
        items = [item for item in items if str(item.get("status")) == status.upper()]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


def list_ledger_entries(settlement_id: str | None = None) -> list[dict[str, Any]]:
    if settlement_id:
        return [entry for entry in settlement_ledger_entries if entry.get("settlement_id") == settlement_id]
    return list(settlement_ledger_entries)
