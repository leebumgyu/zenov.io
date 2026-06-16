from __future__ import annotations

from typing import Any

from .country_config_registry import (
    bootstrap_country_profiles,
    country_config_summary,
    get_country_profile,
    list_country_profiles,
    register_country_profile,
)
from .localization_engine import localized_report_template
from .methodology_adapter import create_methodology_adapter, list_methodology_adapters


def country_dashboard() -> dict[str, Any]:
    countries = list_country_profiles()
    localized_templates = [localized_report_template(item["country_code"]) for item in countries]
    adapters = []
    for item in countries:
        code = item["country_code"]
        if not list_methodology_adapters(code):
            adapters.append(create_methodology_adapter(country_code=code))
        else:
            adapters.extend(list_methodology_adapters(code))
    return {
        "status": "MULTI_COUNTRY_READY",
        "country_count": len(countries),
        "countries": countries,
        "localization_coverage": round((len(localized_templates) / max(len(countries), 1)) * 100, 2),
        "country_specific_template_count": len(localized_templates),
        "methodology_adapter_count": len(adapters),
        "country_onboarding_time_target": "7 days or less by YAML config",
        "rule": "Zenov is a Multi-Country Carbon OS. Trust Layer is shared; country rules are config-driven.",
    }


def add_country_from_config(country_code: str) -> dict[str, Any]:
    profile = register_country_profile(country_code)
    report_template = localized_report_template(country_code)
    adapter = create_methodology_adapter(country_code=country_code)
    return {
        "status": "COUNTRY_CONFIGURED",
        "country": profile,
        "report_template": report_template,
        "methodology_adapter": adapter,
        "message": "Country added through config. No core Trust Layer code change required.",
    }


def country_detail(country_code: str) -> dict[str, Any]:
    profile = get_country_profile(country_code)
    if not profile:
        raise ValueError("COUNTRY_PROFILE_NOT_FOUND")
    return {
        **country_config_summary(country_code),
        "localized_report_template": localized_report_template(country_code),
        "methodology_adapters": list_methodology_adapters(country_code),
    }
