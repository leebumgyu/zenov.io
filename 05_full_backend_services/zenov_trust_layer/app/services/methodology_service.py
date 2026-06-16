from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from ..crypto import canonical_json, sha256_hex
from ..database.methodology_crud import (
    get_methodology,
    list_methodologies,
    list_methodology_impacts,
    save_methodology,
    save_methodology_impact,
    save_methodology_snapshot,
)
from ..storage import carbon_asset_candidates, mrv_reports, taxi_mrv_results
from zenov_mobility.app.services.taxi_mrv_service import load_carbon_factor_config


CONFIG_PATH = Path(__file__).resolve().parents[2] / "zenov_mobility" / "app" / "config" / "carbon_factor.yaml"
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[3] / "zenov_mobility" / "app" / "config" / "carbon_factor.yaml"


def _now_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _load_config() -> dict[str, Any]:
    return load_carbon_factor_config(CONFIG_PATH)


def _methodology_from_config(config: dict[str, Any]) -> dict[str, Any]:
    methodology = config.get("methodology", {})
    methodology_id = str(methodology.get("id", "ZENOV-MOBILITY-MRV-001"))
    version = str(methodology.get("version", "1.0.0"))
    snapshot = {
        "methodology": methodology,
        "emission_factors": config.get("emission_factors", {}),
        "vehicle_efficiency": config.get("vehicle_efficiency", {}),
        "carbon_value": config.get("carbon_value", {}),
        "supported_assets": config.get("supported_assets", {}),
        "formulas": config.get("formulas", {}),
    }
    return {
        "methodology_key": f"{methodology_id}:{version}",
        "methodology_id": methodology_id,
        "version": version,
        "name": methodology_id,
        "description": methodology.get("description", ""),
        "effective_date": methodology.get("effective_date", "2026-06-12"),
        "status": "ACTIVE",
        "source_reference": "zenov_mobility/app/config/carbon_factor.yaml",
        "methodology_hash": sha256_hex(canonical_json(snapshot)),
        "config_snapshot": snapshot,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def register_methodology_from_config() -> dict[str, Any]:
    methodology = _methodology_from_config(_load_config())
    save_methodology(methodology)
    return methodology


def register_methodology(
    *,
    methodology_id: str,
    version: str,
    effective_date: str,
    description: str,
    config_snapshot: dict[str, Any],
    status: str = "ACTIVE",
    source_reference: str = "manual",
) -> dict[str, Any]:
    methodology = {
        "methodology_key": f"{methodology_id}:{version}",
        "methodology_id": methodology_id,
        "version": version,
        "name": methodology_id,
        "description": description,
        "effective_date": effective_date,
        "status": status,
        "source_reference": source_reference,
        "methodology_hash": sha256_hex(canonical_json(config_snapshot)),
        "config_snapshot": config_snapshot,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_methodology(methodology)
    return methodology


def get_registered_methodologies() -> list[dict[str, Any]]:
    items = list_methodologies()
    if not items:
        register_methodology_from_config()
        items = list_methodologies()
    return items


def get_registered_methodology(methodology_id: str, version: str) -> Optional[dict[str, Any]]:
    item = get_methodology(methodology_id, version)
    if item:
        return item
    current = register_methodology_from_config()
    if current["methodology_id"] == methodology_id and current["version"] == version:
        return current
    return None


def create_methodology_snapshot(
    *,
    methodology_id: str,
    methodology_version: str,
    linked_type: str,
    linked_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    snapshot_payload = {
        "methodology_id": methodology_id,
        "methodology_version": methodology_version,
        "linked_type": linked_type,
        "linked_id": linked_id,
        "payload": payload,
    }
    snapshot = {
        "snapshot_id": _now_id("MSNP"),
        "methodology_id": methodology_id,
        "methodology_version": methodology_version,
        "linked_type": linked_type,
        "linked_id": linked_id,
        "snapshot_hash": sha256_hex(canonical_json(snapshot_payload)),
        "snapshot_payload": snapshot_payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_methodology_snapshot(snapshot)
    return snapshot


def _baseline_factor_for(config_snapshot: dict[str, Any], baseline_type: str = "lpg_taxi") -> Optional[float]:
    try:
        return float(config_snapshot["emission_factors"]["baseline"][baseline_type]["value"])
    except (KeyError, TypeError, ValueError):
        return None


def analyze_methodology_change(
    *,
    methodology_id: str,
    from_version: str,
    to_version: str,
    new_config_snapshot: dict[str, Any],
    baseline_type: str = "lpg_taxi",
) -> dict[str, Any]:
    old = get_registered_methodology(methodology_id, from_version)
    if not old:
        raise ValueError("SOURCE_METHODOLOGY_NOT_FOUND")
    old_factor = _baseline_factor_for(old.get("config_snapshot", {}), baseline_type)
    new_factor = _baseline_factor_for(new_config_snapshot, baseline_type)
    affected_mrvs = [
        mrv for mrv in taxi_mrv_results.values()
        if mrv.get("methodology_id") == methodology_id and mrv.get("methodology_version") == from_version
    ]
    affected_reports = [
        report for report in mrv_reports.values()
        if report.get("methodology_id") == methodology_id and report.get("methodology_version") == from_version
    ]
    affected_mrv_ids = {mrv.get("mrv_id") for mrv in affected_mrvs}
    affected_assets = [
        candidate for candidate in carbon_asset_candidates.values()
        if candidate.get("mrv_id") in affected_mrv_ids
    ]

    delta_kg = 0.0
    if old_factor is not None and new_factor is not None:
        for mrv in affected_mrvs:
            distance = float(mrv.get("distance_km", 0) or 0)
            delta_kg += distance * (new_factor - old_factor)

    impact_snapshot = {
        "methodology_id": methodology_id,
        "from_version": from_version,
        "to_version": to_version,
        "baseline_type": baseline_type,
        "baseline_factor_before": old_factor,
        "baseline_factor_after": new_factor,
        "affected_mrv_ids": [mrv.get("mrv_id") for mrv in affected_mrvs],
        "affected_report_ids": [report.get("report_id") for report in affected_reports],
        "affected_asset_ids": [asset.get("candidate_id") for asset in affected_assets],
        "rule": "Existing reports remain immutable. New methodology affects future calculations unless explicit recalculation is approved.",
    }
    impact = {
        "impact_id": _now_id("MIMP"),
        "methodology_id": methodology_id,
        "from_version": from_version,
        "to_version": to_version,
        "affected_mrv_count": len(affected_mrvs),
        "affected_report_count": len(affected_reports),
        "affected_asset_count": len(affected_assets),
        "baseline_factor_before": old_factor,
        "baseline_factor_after": new_factor,
        "estimated_reduction_delta_kgco2e": delta_kg,
        "impact_snapshot": impact_snapshot,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_methodology_impact(impact)
    return impact


def get_methodology_impacts() -> list[dict[str, Any]]:
    return list_methodology_impacts()
