from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from ..database.tenant_crud import get_tenant_subscription, save_subscription


SUBSCRIPTION_PLANS = {
    "FREE": {
        "monthly_fee_krw": 0,
        "seat_limit": 2,
        "vehicle_limit": 10,
        "asset_limit": 5,
        "api_call_limit_monthly": 1000,
        "retention_days": 30,
    },
    "PILOT": {
        "monthly_fee_krw": 500000,
        "seat_limit": 10,
        "vehicle_limit": 200,
        "asset_limit": 500,
        "api_call_limit_monthly": 50000,
        "retention_days": 365,
    },
    "ENTERPRISE": {
        "monthly_fee_krw": 3000000,
        "seat_limit": 100,
        "vehicle_limit": 5000,
        "asset_limit": 50000,
        "api_call_limit_monthly": 2000000,
        "retention_days": 2555,
    },
    "GOVERNMENT": {
        "monthly_fee_krw": 0,
        "seat_limit": 500,
        "vehicle_limit": 100000,
        "asset_limit": 1000000,
        "api_call_limit_monthly": 10000000,
        "retention_days": 3650,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def create_subscription(tenant_id: str, plan: str = "PILOT") -> dict[str, Any]:
    normalized_plan = plan.upper()
    if normalized_plan not in SUBSCRIPTION_PLANS:
        raise ValueError(f"SUBSCRIPTION_PLAN_NOT_SUPPORTED:{plan}")
    existing = get_tenant_subscription(tenant_id)
    if existing:
        return existing
    limits = SUBSCRIPTION_PLANS[normalized_plan]
    subscription = {
        "subscription_id": _new_id("SUB"),
        "tenant_id": tenant_id,
        "plan": normalized_plan,
        "status": "ACTIVE",
        "billing_cycle": "MONTHLY",
        "started_at": _now(),
        "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat() if normalized_plan in {"FREE", "PILOT"} else None,
        **limits,
    }
    save_subscription(subscription)
    return subscription


def get_subscription(tenant_id: str) -> dict[str, Any]:
    subscription = get_tenant_subscription(tenant_id)
    if subscription:
        return subscription
    return create_subscription(tenant_id, "FREE")


def list_subscription_plans() -> dict[str, Any]:
    return {"plans": SUBSCRIPTION_PLANS}
