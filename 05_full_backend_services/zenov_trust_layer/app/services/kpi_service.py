from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any

from ..storage import (
    carbon_asset_candidates,
    mrv_verification_records,
    portfolio_kpi_snapshots,
    portfolio_targets,
    save_portfolio_kpi_snapshot_memory,
)


DEFAULT_PORTFOLIO_ID = "ANSAN_TRANS"
DEFAULT_TARGETS = {
    "portfolio_id": DEFAULT_PORTFOLIO_ID,
    "target_vehicle_count": 500,
    "target_reduction_tco2e": 1000.0,
    "target_asset_count": 300,
    "target_registry_count": 120,
    "target_portfolio_value": 1_000_000_000.0,
    "currency": "KRW",
    "created_at": "2026-06-12T00:00:00+09:00",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _achievement(current: float, target: float) -> float:
    if not target:
        return 0.0
    return round((current / target) * 100, 2)


def _owned_candidates(portfolio_id: str) -> list[dict[str, Any]]:
    return [
        item for item in carbon_asset_candidates.values()
        if str(item.get("owner_entity", portfolio_id)) == portfolio_id
    ]


def _target(portfolio_id: str) -> dict[str, Any]:
    return portfolio_targets.get(portfolio_id) or {**DEFAULT_TARGETS, "portfolio_id": portfolio_id}


def current_portfolio_values(portfolio_id: str = DEFAULT_PORTFOLIO_ID) -> dict[str, Any]:
    candidates = _owned_candidates(portfolio_id)
    vehicle_ids = {item.get("vehicle_id") for item in candidates if item.get("vehicle_id")}
    verified_ids = {
        item.get("verification_id") for item in candidates
        if item.get("verification_id") in mrv_verification_records
    }
    scores = [
        float(mrv_verification_records[verification_id].get("verification_score", 0))
        for verification_id in verified_ids
    ]
    registry_count = sum(1 for item in candidates if item.get("registry_status") in {"SUBMITTED", "REGISTERED", "RETIRED"})
    return {
        "portfolio_id": portfolio_id,
        "fleet_size": len(vehicle_ids),
        "verified_reduction_tco2e": round(sum(float(item.get("issued_quantity_tco2e", 0) or 0) for item in candidates), 6),
        "asset_count": len(candidates),
        "registry_count": registry_count,
        "portfolio_value_krw": round(sum(float(item.get("estimated_value_krw", 0) or 0) for item in candidates), 2),
        "average_verification_score": round(mean(scores), 2) if scores else 0,
    }


def portfolio_kpi(portfolio_id: str = DEFAULT_PORTFOLIO_ID) -> dict[str, Any]:
    target = _target(portfolio_id)
    current = current_portfolio_values(portfolio_id)
    metrics = {
        "fleet_size": {
            "current_value": current["fleet_size"],
            "target_value": target["target_vehicle_count"],
            "achievement_rate": _achievement(current["fleet_size"], float(target["target_vehicle_count"])),
            "trend": "UP" if current["fleet_size"] > 0 else "FLAT",
        },
        "carbon_reduction": {
            "current_value": current["verified_reduction_tco2e"],
            "target_value": target["target_reduction_tco2e"],
            "unit": "tCO2e",
            "achievement_rate": _achievement(current["verified_reduction_tco2e"], float(target["target_reduction_tco2e"])),
            "trend": "UP" if current["verified_reduction_tco2e"] > 0 else "FLAT",
        },
        "asset_creation": {
            "current_value": current["asset_count"],
            "target_value": target["target_asset_count"],
            "achievement_rate": _achievement(current["asset_count"], float(target["target_asset_count"])),
            "trend": "UP" if current["asset_count"] > 0 else "FLAT",
        },
        "registry_assets": {
            "current_value": current["registry_count"],
            "target_value": target["target_registry_count"],
            "achievement_rate": _achievement(current["registry_count"], float(target["target_registry_count"])),
            "trend": "FLAT",
        },
        "portfolio_value": {
            "current_value": current["portfolio_value_krw"],
            "target_value": target["target_portfolio_value"],
            "currency": target.get("currency", "KRW"),
            "achievement_rate": _achievement(current["portfolio_value_krw"], float(target["target_portfolio_value"])),
            "trend": "UP" if current["portfolio_value_krw"] > 0 else "FLAT",
        },
    }
    return {
        "portfolio_id": portfolio_id,
        "generated_at": _now(),
        "current": current,
        "target": target,
        "metrics": metrics,
        "executive_summary": {
            "fleet_size": f"{current['fleet_size']} / {target['target_vehicle_count']}",
            "verified_reduction": f"{current['verified_reduction_tco2e']} / {target['target_reduction_tco2e']} tCO2e",
            "asset_creation": f"{current['asset_count']} / {target['target_asset_count']}",
            "portfolio_value": f"{current['portfolio_value_krw']} / {target['target_portfolio_value']} KRW",
        },
    }


def save_kpi_snapshot(period: str = "DAILY", portfolio_id: str = DEFAULT_PORTFOLIO_ID) -> dict[str, Any]:
    snapshot = {
        "snapshot_id": f"KPI-{period}-{portfolio_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "period": period,
        "portfolio_id": portfolio_id,
        "snapshot": portfolio_kpi(portfolio_id),
        "created_at": _now(),
    }
    save_portfolio_kpi_snapshot_memory(snapshot)
    return snapshot


def list_kpi_snapshots(portfolio_id: str = DEFAULT_PORTFOLIO_ID) -> list[dict[str, Any]]:
    return [
        item for item in portfolio_kpi_snapshots.values()
        if item.get("portfolio_id") == portfolio_id
    ]
