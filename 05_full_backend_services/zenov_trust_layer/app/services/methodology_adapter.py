from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import country_methodology_adapters, save_country_methodology_adapter_memory
from .country_config_registry import get_country_profile


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def create_methodology_adapter(
    *,
    country_code: str,
    industry_type: str = "TAXI",
    base_methodology_id: str = "ZENOV-MOBILITY-MRV-001",
    local_methodology_id: str | None = None,
    local_methodology_version: str = "draft",
    adapter_status: str = "DRAFT",
) -> dict[str, Any]:
    profile = get_country_profile(country_code)
    if not profile:
        raise ValueError("COUNTRY_PROFILE_NOT_FOUND")
    code = profile["country_code"]
    config = profile["config_snapshot"]
    local_id = local_methodology_id or f"{base_methodology_id}-{code}"
    adapter = {
        "adapter_id": _new_id("MADAPT"),
        "country_code": code,
        "industry_type": industry_type.upper(),
        "base_methodology_id": base_methodology_id,
        "local_methodology_id": local_id,
        "local_methodology_version": local_methodology_version,
        "adapter_status": adapter_status,
        "rules": {
            "grid_emission_factor": config.get("carbon", {}).get("grid_emission_factor", {}),
            "fuel_emission_factors": config.get("carbon", {}).get("fuel_emission_factors", {}),
            "registry": config.get("registry", {}),
            "report_language": config.get("report", {}).get("language"),
        },
        "created_at": _now(),
    }
    save_country_methodology_adapter_memory(adapter)
    return adapter


def list_methodology_adapters(country_code: str | None = None) -> list[dict[str, Any]]:
    items = list(country_methodology_adapters.values())
    if country_code:
        items = [item for item in items if item.get("country_code") == country_code.upper()]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)
