from __future__ import annotations

from typing import Any

from ..storage import localized_report_templates, save_localized_report_template_memory
from .country_config_registry import get_country_profile


def localized_report_template(country_code: str, report_type: str = "ANNUAL_MRV") -> dict[str, Any]:
    profile = get_country_profile(country_code)
    if not profile:
        raise ValueError("COUNTRY_PROFILE_NOT_FOUND")
    config = profile["config_snapshot"]
    report = config.get("report", {})
    code = profile["country_code"]
    template_id = f"RPT-TPL-{code}-{report_type}"
    template = {
        "template_id": template_id,
        "country_code": code,
        "report_type": report_type,
        "language_code": report.get("language", profile.get("language_code")),
        "unit_system": report.get("unit_system", "METRIC"),
        "template_version": "1.0.0",
        "required_sections": report.get("required_sections", []),
        "labels": report.get("labels", {}),
        "currency_code": profile.get("currency_code"),
        "timezone": profile.get("timezone"),
        "status": "CONFIGURED",
    }
    save_localized_report_template_memory(template)
    return template


def localize_report_snapshot(country_code: str, report_snapshot: dict[str, Any]) -> dict[str, Any]:
    template = localized_report_template(country_code)
    labels = template.get("labels", {})
    return {
        "country_code": country_code.upper(),
        "language_code": template["language_code"],
        "currency_code": template["currency_code"],
        "timezone": template["timezone"],
        "report_type": template["report_type"],
        "localized_labels": labels,
        "required_sections": template["required_sections"],
        "source_report_snapshot": report_snapshot,
        "localization_status": "READY",
    }


def list_localized_templates() -> list[dict[str, Any]]:
    return sorted(localized_report_templates.values(), key=lambda item: item.get("template_id", ""))
