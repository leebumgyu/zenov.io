from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import (
    merchant_accounts,
    save_merchant_account_memory,
    save_settlement_batch_memory,
)
from .settlement_ledger import list_settlement_records


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def find_merchant_account(merchant_id: str, tenant_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    for account in merchant_accounts.values():
        if account.get("merchant_id") == merchant_id and account.get("tenant_id") == tenant_id:
            return account
    return None


def ensure_merchant_account(
    *,
    merchant_id: str,
    merchant_name: str,
    merchant_type: str = "CHARGING",
    tenant_id: Optional[str] = None,
    settlement_currency: str = "KRW",
) -> dict[str, Any]:
    existing = find_merchant_account(merchant_id, tenant_id)
    if existing:
        return existing
    account = {
        "merchant_account_id": _new_id("MCH"),
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "merchant_type": merchant_type,
        "tenant_id": tenant_id,
        "settlement_currency": settlement_currency,
        "status": "ACTIVE",
        "metadata": {},
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_merchant_account_memory(account)
    return account


def list_merchant_accounts(tenant_id: Optional[str] = None) -> list[dict[str, Any]]:
    items = list(merchant_accounts.values())
    if tenant_id:
        items = [item for item in items if str(item.get("tenant_id")) == tenant_id]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


def simulate_settlement_batch(tenant_id: Optional[str] = None, batch_period: str = "DAILY") -> dict[str, Any]:
    records = [
        record for record in list_settlement_records(tenant_id=tenant_id)
        if record.get("status") in {"PENDING", "APPROVED"}
    ]
    batch = {
        "batch_id": _new_id("SBATCH"),
        "tenant_id": tenant_id,
        "batch_period": batch_period,
        "status": "PENDING",
        "record_count": len(records),
        "total_gross_amount_krw": round(sum(float(item.get("gross_amount_krw", 0) or 0) for item in records), 2),
        "total_fee_krw": round(sum(float(item.get("total_fee_krw", 0) or 0) for item in records), 2),
        "total_net_amount_krw": round(sum(float(item.get("net_amount_krw", 0) or 0) for item in records), 2),
        "simulation_only": True,
        "record_ids": [item["settlement_id"] for item in records],
        "created_at": _now(),
    }
    save_settlement_batch_memory(batch)
    return batch
