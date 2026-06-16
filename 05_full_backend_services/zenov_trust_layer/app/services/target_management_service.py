from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..storage import portfolio_targets, save_portfolio_target_memory
from .kpi_service import DEFAULT_PORTFOLIO_ID, DEFAULT_TARGETS


def upsert_portfolio_target(
    *,
    portfolio_id: str = DEFAULT_PORTFOLIO_ID,
    target_vehicle_count: int = 500,
    target_reduction_tco2e: float = 1000.0,
    target_asset_count: int = 300,
    target_registry_count: int = 120,
    target_portfolio_value: float = 1_000_000_000.0,
    currency: str = "KRW",
) -> dict[str, Any]:
    target = {
        "portfolio_id": portfolio_id,
        "target_vehicle_count": target_vehicle_count,
        "target_reduction_tco2e": target_reduction_tco2e,
        "target_asset_count": target_asset_count,
        "target_registry_count": target_registry_count,
        "target_portfolio_value": target_portfolio_value,
        "currency": currency,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_portfolio_target_memory(target)
    return target


def get_portfolio_target(portfolio_id: str = DEFAULT_PORTFOLIO_ID) -> dict[str, Any]:
    return portfolio_targets.get(portfolio_id) or {**DEFAULT_TARGETS, "portfolio_id": portfolio_id}
