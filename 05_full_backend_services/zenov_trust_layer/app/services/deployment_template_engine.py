from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import deployment_templates, save_deployment_template_memory


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


DEFAULT_TEMPLATES = [
    {
        "template_id": "TPL-TAXI-TMONEY-CSV",
        "industry_type": "TAXI",
        "template_name": "Taxi T-money CSV Onboarding",
        "connector_type": "CSV_IMPORT",
        "supported_sources": ["TMONEY_CSV", "TAXI_METER", "DTG", "GPS", "CHARGER"],
        "required_fields": ["vehicle_id", "operation_date", "distance_km", "passenger_count", "daily_revenue", "driver_id"],
        "validation_rules": ["vehicle_id_required", "operation_date_valid", "distance_non_negative", "duplicate_vehicle_date_blocked"],
        "default_mapping": {
            "차량번호": "vehicle_id",
            "운행일": "operation_date",
            "주행거리": "distance_km",
            "승객수": "passenger_count",
            "매출": "daily_revenue",
            "기사ID": "driver_id",
        },
    },
    {
        "template_id": "TPL-BUS-OPERATION-API",
        "industry_type": "BUS",
        "template_name": "EV Bus Operation API Onboarding",
        "connector_type": "REST_API",
        "supported_sources": ["BUS_OPERATION_API", "CHARGER", "GPS"],
        "required_fields": ["vehicle_id", "route_id", "operation_date", "distance_km", "energy_consumed_kwh"],
        "validation_rules": ["route_id_required", "distance_non_negative", "energy_non_negative"],
        "default_mapping": {},
    },
    {
        "template_id": "TPL-SOLAR-INVERTER",
        "industry_type": "SOLAR",
        "template_name": "Solar Inverter Data Onboarding",
        "connector_type": "API_OR_CSV",
        "supported_sources": ["INVERTER_API", "CSV_IMPORT", "METER"],
        "required_fields": ["solar_site_id", "solar_generation_kwh", "self_consumption_kwh", "grid_export_kwh", "timestamp"],
        "validation_rules": ["self_consumption_lte_generation", "export_lte_generation", "timestamp_required"],
        "default_mapping": {},
    },
]


def bootstrap_deployment_templates() -> list[dict[str, Any]]:
    created = []
    for template in DEFAULT_TEMPLATES:
        item = dict(template)
        item.update({
            "status": "ACTIVE",
            "version": "1.0.0",
            "created_at": item.get("created_at") or _now(),
        })
        save_deployment_template_memory(item)
        created.append(item)
    return created


def list_deployment_templates(industry_type: Optional[str] = None) -> list[dict[str, Any]]:
    if not deployment_templates:
        bootstrap_deployment_templates()
    items = list(deployment_templates.values())
    if industry_type:
        items = [item for item in items if item.get("industry_type") == industry_type.upper()]
    return sorted(items, key=lambda item: item.get("template_id", ""))


def get_deployment_template(template_id: str) -> Optional[dict[str, Any]]:
    if not deployment_templates:
        bootstrap_deployment_templates()
    return deployment_templates.get(template_id)


def create_deployment_template(
    *,
    industry_type: str,
    template_name: str,
    connector_type: str,
    supported_sources: Optional[list[str]] = None,
    required_fields: Optional[list[str]] = None,
    validation_rules: Optional[list[str]] = None,
    default_mapping: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    template = {
        "template_id": _new_id("TPL"),
        "industry_type": industry_type.upper(),
        "template_name": template_name,
        "connector_type": connector_type.upper(),
        "supported_sources": supported_sources or [],
        "required_fields": required_fields or [],
        "validation_rules": validation_rules or [],
        "default_mapping": default_mapping or {},
        "status": "ACTIVE",
        "version": "1.0.0",
        "created_at": _now(),
    }
    save_deployment_template_memory(template)
    return template
