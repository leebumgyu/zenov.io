from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..database.tenant_crud import get_billing_account, save_billing_account
from .subscription_service import get_subscription


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def create_billing_account(tenant_id: str, billing_email: Optional[str] = None, currency: str = "KRW") -> dict[str, Any]:
    existing = get_billing_account(tenant_id)
    if existing:
        return existing
    subscription = get_subscription(tenant_id)
    account = {
        "billing_account_id": _new_id("BILL"),
        "tenant_id": tenant_id,
        "billing_email": billing_email,
        "currency": currency,
        "payment_status": "TRIAL" if subscription.get("trial_ends_at") else "ACTIVE",
        "current_balance_krw": 0,
        "monthly_fee_krw": subscription["monthly_fee_krw"],
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_billing_account(account)
    return account


def billing_summary(tenant_id: str) -> dict[str, Any]:
    account = get_billing_account(tenant_id) or create_billing_account(tenant_id)
    subscription = get_subscription(tenant_id)
    return {
        "tenant_id": tenant_id,
        "billing_account": account,
        "subscription": subscription,
        "next_invoice_estimate_krw": subscription["monthly_fee_krw"],
        "currency": account["currency"],
    }
