from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import (
    asset_ownership_records,
    asset_transfer_records,
    carbon_asset_candidates,
    save_asset_ownership_memory,
)
from .custody_service import DEFAULT_CUSTODIAN_ENTITY, DEFAULT_CUSTODIAN_TYPE, ensure_custody
from .ownership_audit_service import list_ownership_audit, record_ownership_event


OWNER_TYPES = {
    "Driver",
    "Fleet Company",
    "Project Owner",
    "Partner Company",
    "Zenov Asset Pool",
    "Government Program",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _find_asset(asset_id: str) -> dict[str, Any] | None:
    if asset_id in carbon_asset_candidates:
        return carbon_asset_candidates[asset_id]
    return next(
        (
            item for item in carbon_asset_candidates.values()
            if item.get("serial_number") == asset_id or item.get("registry_id") == asset_id
        ),
        None,
    )


def _owner_type_for(owner_entity: str) -> str:
    owner = str(owner_entity or "").upper()
    if owner.startswith("DRV"):
        return "Driver"
    if "GOV" in owner or "MINISTRY" in owner:
        return "Government Program"
    if "ZENOV" in owner:
        return "Zenov Asset Pool"
    if "PARTNER" in owner:
        return "Partner Company"
    return "Fleet Company"


def ensure_asset_ownership(asset_id: str) -> dict[str, Any]:
    asset = _find_asset(asset_id)
    if not asset:
        raise ValueError("ASSET_NOT_FOUND")
    resolved_asset_id = asset["candidate_id"]
    existing = asset_ownership_records.get(resolved_asset_id)
    if existing:
        return existing
    owner_entity = str(asset.get("owner_entity") or "ZENOV_ASSET_POOL")
    ownership = {
        "ownership_id": _new_id("OWN"),
        "asset_id": resolved_asset_id,
        "serial_number": asset.get("serial_number"),
        "owner_entity": owner_entity,
        "owner_type": _owner_type_for(owner_entity),
        "owner_country": "KR",
        "custodian_entity": DEFAULT_CUSTODIAN_ENTITY,
        "custodian_type": DEFAULT_CUSTODIAN_TYPE,
        "custody_status": "HELD",
        "ownership_status": "ACTIVE",
        "acquired_at": asset.get("created_at") or _now(),
        "retired_at": None,
        "asset_snapshot": asset,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_asset_ownership_memory(ownership)
    ensure_custody(resolved_asset_id)
    record_ownership_event(
        asset_id=resolved_asset_id,
        event_type="OWNERSHIP_REGISTERED",
        event_status="ACTIVE",
        message=f"Initial ownership registered to {owner_entity}.",
        snapshot=ownership,
    )
    return ownership


def get_asset_ownership(asset_id: str) -> dict[str, Any]:
    ownership = ensure_asset_ownership(asset_id)
    asset_id = ownership["asset_id"]
    custody = ensure_custody(asset_id)
    transfers = list_asset_history(asset_id)["transfers"]
    return {
        "asset_id": asset_id,
        "ownership": ownership,
        "current_owner": {
            "owner_entity": ownership["owner_entity"],
            "owner_type": ownership["owner_type"],
            "owner_country": ownership.get("owner_country"),
        },
        "custody": custody,
        "transfer_count": len(transfers),
        "chain_of_ownership": build_chain_of_ownership(asset_id),
        "rule": "Every asset must have a current owner, a custodian, and a transfer history.",
    }


def build_chain_of_ownership(asset_id: str) -> list[dict[str, Any]]:
    ownership = asset_ownership_records.get(asset_id) or ensure_asset_ownership(asset_id)
    transfers = [
        item for item in asset_transfer_records.values()
        if item.get("asset_id") == asset_id
    ]
    transfers = sorted(transfers, key=lambda item: item.get("transferred_at", ""))
    chain: list[dict[str, Any]] = []
    if not transfers:
        chain.append({
            "sequence": 1,
            "owner_entity": ownership["owner_entity"],
            "owner_type": ownership["owner_type"],
            "event_type": "INITIAL_OWNER",
            "event_at": ownership["acquired_at"],
        })
        return chain
    first = transfers[0]
    chain.append({
        "sequence": 1,
        "owner_entity": first["from_owner_entity"],
        "owner_type": first["from_owner_type"],
        "event_type": "INITIAL_OWNER",
        "event_at": ownership["created_at"],
    })
    for index, transfer in enumerate(transfers, start=2):
        chain.append({
            "sequence": index,
            "owner_entity": transfer["to_owner_entity"],
            "owner_type": transfer["to_owner_type"],
            "event_type": transfer["transfer_status"],
            "event_at": transfer["transferred_at"],
            "transfer_id": transfer["transfer_id"],
            "transfer_reason": transfer["transfer_reason"],
        })
    return chain


def list_asset_history(asset_id: str) -> dict[str, Any]:
    ownership = ensure_asset_ownership(asset_id)
    resolved_asset_id = ownership["asset_id"]
    transfers = [
        item for item in asset_transfer_records.values()
        if item.get("asset_id") == resolved_asset_id
    ]
    return {
        "asset_id": resolved_asset_id,
        "ownership": ownership,
        "transfers": sorted(transfers, key=lambda item: item.get("transferred_at", ""), reverse=True),
        "audits": list_ownership_audit(resolved_asset_id),
        "chain_of_ownership": build_chain_of_ownership(resolved_asset_id),
    }


def ownership_summary() -> dict[str, Any]:
    for asset_id in list(carbon_asset_candidates.keys()):
        ensure_asset_ownership(asset_id)
    owners = {}
    for record in asset_ownership_records.values():
        owners[record["owner_entity"]] = owners.get(record["owner_entity"], 0) + 1
    return {
        "asset_count": len(asset_ownership_records),
        "custodied_asset_count": len(asset_ownership_records),
        "transfer_count": len(asset_transfer_records),
        "owner_count": len(owners),
        "owners": owners,
        "global_ownership_status": "ACTIVE" if asset_ownership_records else "NO_ASSETS",
    }
