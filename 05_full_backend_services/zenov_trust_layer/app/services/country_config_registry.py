from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..crypto import canonical_json, sha256_hex
from ..storage import country_profiles, save_country_profile_memory
from .config_loader import load_yaml_config


COUNTRY_CONFIG_DIR = Path(__file__).resolve().parents[1] / "config" / "countries"
SUPPORTED_COUNTRIES = ["KR", "TH", "MY", "ID", "VN"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_country_config(country_code: str) -> dict[str, Any]:
    code = country_code.upper()
    path = COUNTRY_CONFIG_DIR / f"{code}.yaml"
    fallback = {
        "country": {
            "code": code,
            "name": code,
            "language": "en",
            "currency": "USD",
            "timezone": "UTC",
            "profile_version": "draft",
        },
        "carbon": {
            "grid_emission_factor": {
                "value": 0,
                "unit": "kgCO2e/kWh",
                "source": "NOT_CONFIGURED",
                "source_version": "draft",
                "effective_date": "2026-06-12",
            },
            "fuel_emission_factors": {},
            "methodologies": [],
        },
        "registry": {
            "local_registry": "NOT_CONFIGURED",
            "government_reporting_format": "NOT_CONFIGURED",
            "submission_language": "en",
        },
        "report": {
            "language": "en",
            "unit_system": "METRIC",
            "labels": {},
            "required_sections": [],
        },
    }
    return load_yaml_config(path, fallback)


def register_country_profile(country_code: str) -> dict[str, Any]:
    config = load_country_config(country_code)
    country = config.get("country", {})
    code = str(country.get("code", country_code)).upper()
    profile = {
        "country_code": code,
        "country_name": country.get("name", code),
        "language_code": country.get("language", "en"),
        "currency_code": country.get("currency", "USD"),
        "timezone": country.get("timezone", "UTC"),
        "status": "ACTIVE",
        "profile_version": str(country.get("profile_version", "1.0.0")),
        "config_hash": sha256_hex(canonical_json(config)),
        "config_snapshot": config,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_country_profile_memory(profile)
    return profile


def bootstrap_country_profiles() -> list[dict[str, Any]]:
    return [register_country_profile(code) for code in SUPPORTED_COUNTRIES]


def list_country_profiles() -> list[dict[str, Any]]:
    if not country_profiles:
        bootstrap_country_profiles()
    return sorted(country_profiles.values(), key=lambda item: item.get("country_code", ""))


def get_country_profile(country_code: str) -> Optional[dict[str, Any]]:
    code = country_code.upper()
    if code not in country_profiles:
        register_country_profile(code)
    return country_profiles.get(code)


def country_config_summary(country_code: str) -> dict[str, Any]:
    profile = get_country_profile(country_code)
    if not profile:
        raise ValueError("COUNTRY_PROFILE_NOT_FOUND")
    config = profile["config_snapshot"]
    carbon = config.get("carbon", {})
    registry = config.get("registry", {})
    report = config.get("report", {})
    return {
        "country": profile,
        "carbon_profile": {
            "grid_emission_factor": carbon.get("grid_emission_factor", {}),
            "fuel_emission_factor_count": len(carbon.get("fuel_emission_factors", {}) or {}),
            "mrv_methodologies": carbon.get("methodologies", []),
        },
        "registry_profile": registry,
        "report_profile": {
            "language": report.get("language"),
            "unit_system": report.get("unit_system"),
            "required_sections": report.get("required_sections", []),
        },
        "rule": "Add a country by adding a YAML config. Core Trust Layer code stays shared.",
    }
