from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from .commission_engine import calculate_commission, default_commission_rule
from .merchant_settlement import ensure_merchant_account
from .settlement_ledger import save_settlement_record


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def simulate_offer_redeem(
    *,
    tenant_id: Optional[str],
    driver_id: str,
    offer_id: str,
    merchant_id: str,
    merchant_name: str,
    merchant_type: str = "CHARGING",
    gross_amount_krw: float,
    point_amount: float = 0,
    wallet_transaction_id: Optional[str] = None,
) -> dict[str, Any]:
    if gross_amount_krw < 0:
        raise ValueError("NEGATIVE_GROSS_AMOUNT")
    merchant = ensure_merchant_account(
        merchant_id=merchant_id,
        merchant_name=merchant_name,
        merchant_type=merchant_type,
        tenant_id=tenant_id,
    )
    rule = default_commission_rule(tenant_id)
    fees = calculate_commission(gross_amount_krw, rule)
    trace_snapshot = {
        "driver_id": driver_id,
        "offer_id": offer_id,
        "merchant_id": merchant_id,
        "merchant_account_id": merchant["merchant_account_id"],
        "wallet_transaction_id": wallet_transaction_id,
        "commission_rule_id": rule["rule_id"],
        "simulation_only": True,
        "message": "Driver -> Offer Redeem -> Merchant -> Settlement Record",
    }
    record = {
        "settlement_id": _new_id("SETTLE"),
        "tenant_id": tenant_id,
        "driver_id": driver_id,
        "wallet_transaction_id": wallet_transaction_id,
        "offer_id": offer_id,
        "merchant_account_id": merchant["merchant_account_id"],
        "merchant": merchant,
        "gross_amount_krw": fees["gross_amount_krw"],
        "marketplace_fee_krw": fees["marketplace_fee_krw"],
        "partner_fee_krw": fees["partner_fee_krw"],
        "platform_fee_krw": fees["platform_fee_krw"],
        "fixed_fee_krw": fees["fixed_fee_krw"],
        "total_fee_krw": fees["total_fee_krw"],
        "net_amount_krw": fees["net_amount_krw"],
        "point_amount": float(point_amount or 0),
        "status": "PENDING",
        "simulation_only": True,
        "commission_rule": rule,
        "trace_snapshot": trace_snapshot,
        "created_at": _now(),
        "approved_at": None,
        "settled_at": None,
        "reversed_at": None,
        "cancelled_at": None,
    }
    save_settlement_record(record)
    return {
        "status": "SIMULATED",
        "settlement": record,
        "rule": "No real financial transaction was executed. This is settlement simulation and ledger only.",
    }
