from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import commission_rules, save_commission_rule_memory


DEFAULT_MARKETPLACE_FEE_RATE = 0.03
DEFAULT_PARTNER_FEE_RATE = 0.02
DEFAULT_PLATFORM_FEE_RATE = 0.05
DEFAULT_FIXED_FEE_KRW = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def default_commission_rule(tenant_id: Optional[str] = None) -> dict[str, Any]:
    rule_id = f"COMMISSION-RULE-{tenant_id or 'DEFAULT'}"
    existing = commission_rules.get(rule_id)
    if existing:
        return existing
    rule = {
        "rule_id": rule_id,
        "tenant_id": tenant_id,
        "marketplace_fee_rate": DEFAULT_MARKETPLACE_FEE_RATE,
        "partner_fee_rate": DEFAULT_PARTNER_FEE_RATE,
        "platform_fee_rate": DEFAULT_PLATFORM_FEE_RATE,
        "fixed_fee_krw": DEFAULT_FIXED_FEE_KRW,
        "currency": "KRW",
        "status": "ACTIVE",
        "effective_date": datetime.now(timezone.utc).date().isoformat(),
        "source": "ZENOV_INTERNAL_SIMULATION",
        "version": "draft",
        "created_at": _now(),
    }
    save_commission_rule_memory(rule)
    return rule


def create_commission_rule(
    *,
    tenant_id: Optional[str] = None,
    marketplace_fee_rate: float = DEFAULT_MARKETPLACE_FEE_RATE,
    partner_fee_rate: float = DEFAULT_PARTNER_FEE_RATE,
    platform_fee_rate: float = DEFAULT_PLATFORM_FEE_RATE,
    fixed_fee_krw: float = DEFAULT_FIXED_FEE_KRW,
    source: str = "ZENOV_INTERNAL_SIMULATION",
    version: str = "draft",
) -> dict[str, Any]:
    rule = {
        "rule_id": _new_id("CRULE"),
        "tenant_id": tenant_id,
        "marketplace_fee_rate": float(marketplace_fee_rate),
        "partner_fee_rate": float(partner_fee_rate),
        "platform_fee_rate": float(platform_fee_rate),
        "fixed_fee_krw": float(fixed_fee_krw),
        "currency": "KRW",
        "status": "ACTIVE",
        "effective_date": datetime.now(timezone.utc).date().isoformat(),
        "source": source,
        "version": version,
        "created_at": _now(),
    }
    save_commission_rule_memory(rule)
    return rule


def calculate_commission(gross_amount_krw: float, rule: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    applied_rule = rule or default_commission_rule()
    gross = max(0.0, float(gross_amount_krw or 0))
    marketplace_fee = round(gross * float(applied_rule.get("marketplace_fee_rate", 0) or 0), 2)
    partner_fee = round(gross * float(applied_rule.get("partner_fee_rate", 0) or 0), 2)
    platform_fee = round(gross * float(applied_rule.get("platform_fee_rate", 0) or 0), 2)
    fixed_fee = round(float(applied_rule.get("fixed_fee_krw", 0) or 0), 2)
    total_fee = round(marketplace_fee + partner_fee + platform_fee + fixed_fee, 2)
    net_amount = round(max(0.0, gross - total_fee), 2)
    return {
        "rule_id": applied_rule["rule_id"],
        "gross_amount_krw": gross,
        "marketplace_fee_krw": marketplace_fee,
        "partner_fee_krw": partner_fee,
        "platform_fee_krw": platform_fee,
        "fixed_fee_krw": fixed_fee,
        "total_fee_krw": total_fee,
        "net_amount_krw": net_amount,
        "currency": applied_rule.get("currency", "KRW"),
        "simulation_only": True,
    }
