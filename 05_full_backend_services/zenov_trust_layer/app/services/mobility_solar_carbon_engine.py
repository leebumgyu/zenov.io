from pathlib import Path
from typing import Any, Optional

from .config_loader import load_yaml_config


CONFIG_VERSION = "CARBON_FACTOR_CONFIG_V1.0"
METHODOLOGY_VERSION = "MRV_ENGINE_MOBILITY_SOLAR_V1.0"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "carbon-factor-config.yaml"

DEFAULT_CONFIG = {
    "version": CONFIG_VERSION,
    "effective_date": "2026-06-19",
    "currency": "KRW",
    "global": {
        "grid_emission_factor": {"value": 0.45},
        "carbon_price": {
            "value": 17000,
            "source": "PREMIUM_GS_SCENARIO",
            "price_date": "2026-06-19",
        },
    },
    "mobility": {
        "ev_taxi": {"baseline_vehicle": {"emission_factor": {"value": 0.25}}},
        "ev_bus": {"baseline_vehicle": {"emission_factor": {"value": 0.85}}},
        "ev_motorcycle": {"baseline_vehicle": {"emission_factor": {"value": 0.07}}},
    },
    "solar": {
        "rooftop_solar": {
            "required_fields": ["solar_generation_kwh", "self_consumption_kwh", "grid_export_kwh"],
        }
    },
    "reward": {
        "green_point": {
            "point_per_kg_co2e": {"value": 10},
        }
    },
    "revenue": {
        "base_platform_fee": {"value": 1000000},
        "mrv_service_fee": {"value": 500000},
        "data_management_fee": {"value": 500000},
        "setup_fee": {"value": 20000000},
        "contract_months": {"value": 12},
    },
    "project_assumptions": {
        "ev_taxi": {
            "annual_distance_km_per_vehicle": {"value": 20000},
            "annual_charging_kwh_per_vehicle": {"value": 3600},
            "annual_solar_self_consumption_kwh_per_vehicle": {"value": 0},
        }
    },
}

MOBILITY_SOURCE_MAP = {
    "EV_TAXI": "ev_taxi",
    "EV_BUS": "ev_bus",
    "EV_MOTORCYCLE": "ev_motorcycle",
    "EV_MC": "ev_motorcycle",
}


class MobilitySolarCarbonError(ValueError):
    pass


def get_carbon_factor_config() -> dict[str, Any]:
    return load_yaml_config(CONFIG_PATH, DEFAULT_CONFIG)


def _required(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if payload.get(field) is None]
    if missing:
        raise MobilitySolarCarbonError(f"REQUIRED_FIELD_MISSING:{','.join(missing)}")


def _carbon_value(config: dict[str, Any], reduction_tco2e: float) -> dict[str, Any]:
    price = config["global"]["carbon_price"]
    carbon_price_per_ton = float(price["value"])
    return {
        "estimated_value": reduction_tco2e * carbon_price_per_ton,
        "currency": config.get("currency", "KRW"),
        "carbon_price_per_ton": carbon_price_per_ton,
        "price_source": price.get("source"),
        "price_date": price.get("price_date"),
    }


def calculate_project_revenue(config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    active_config = config or get_carbon_factor_config()
    revenue = active_config.get("revenue") or DEFAULT_CONFIG["revenue"]
    base_platform_fee = float((revenue.get("base_platform_fee") or {}).get("value") or 0)
    mrv_service_fee = float((revenue.get("mrv_service_fee") or {}).get("value") or 0)
    data_management_fee = float((revenue.get("data_management_fee") or {}).get("value") or 0)
    setup_fee = float((revenue.get("setup_fee") or {}).get("value") or 0)
    contract_months = int(float((revenue.get("contract_months") or {}).get("value") or 12))
    monthly_service_revenue = base_platform_fee + mrv_service_fee + data_management_fee
    project_revenue = setup_fee + monthly_service_revenue * contract_months
    return {
        "base_platform_fee": base_platform_fee,
        "mrv_service_fee": mrv_service_fee,
        "data_management_fee": data_management_fee,
        "setup_fee": setup_fee,
        "contract_months": contract_months,
        "monthly_service_revenue": monthly_service_revenue,
        "project_revenue": project_revenue,
        "arr": monthly_service_revenue * 12,
    }


def _base_output(config: dict[str, Any], payload: dict[str, Any], reduction_kgco2e: float) -> dict[str, Any]:
    reduction_tco2e = reduction_kgco2e / 1000
    value = _carbon_value(config, reduction_tco2e)
    return {
        "carbon_project_id": payload.get("carbon_project_id", "CPJ-KR-20260619-000001"),
        "asset_id": payload.get("asset_id") or payload.get("vehicle_id") or payload.get("solar_site_id"),
        "source_type": payload["source_type"],
        "reduction_kgco2e": reduction_kgco2e,
        "reduction_tco2e": reduction_tco2e,
        "estimated_value": value["estimated_value"],
        "currency": value["currency"],
        "methodology_version": METHODOLOGY_VERSION,
        "factor_config_version": config.get("version", CONFIG_VERSION),
        "carbon_price_per_ton": value["carbon_price_per_ton"],
        "price_source": value["price_source"],
        "price_date": value["price_date"],
    }


def calculate_ev_taxi_solar_reduction(payload: dict[str, Any], config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    active_config = config or get_carbon_factor_config()
    _required(payload, ["distance_km", "charging_kwh"])
    distance_km = float(payload["distance_km"])
    charging_kwh = float(payload["charging_kwh"])
    solar_self_consumption_kwh = float(payload.get("solar_self_consumption_kwh") or 0)
    solar_generation_kwh = float(payload.get("solar_generation_kwh") or solar_self_consumption_kwh)
    if min(distance_km, charging_kwh, solar_self_consumption_kwh, solar_generation_kwh) < 0:
        raise MobilitySolarCarbonError("NEGATIVE_INPUT_NOT_ALLOWED")
    if solar_self_consumption_kwh > solar_generation_kwh:
        raise MobilitySolarCarbonError("VALIDATION_FAILED:solar_self_consumption_kwh <= solar_generation_kwh")

    source_config = active_config["mobility"]["ev_taxi"]
    diesel_factor = float(source_config["baseline_vehicle"]["emission_factor"]["value"])
    grid_factor = float(active_config["global"]["grid_emission_factor"]["value"])
    solar_used_for_charging_kwh = min(solar_self_consumption_kwh, charging_kwh)
    grid_charging_kwh = charging_kwh - solar_used_for_charging_kwh
    baseline_emission = distance_km * diesel_factor
    actual_emission = grid_charging_kwh * grid_factor
    solar_reduction = solar_used_for_charging_kwh * grid_factor
    total_reduction = baseline_emission - actual_emission

    normalized_payload = {**payload, "source_type": "EV_TAXI"}
    output = _base_output(active_config, normalized_payload, total_reduction)
    output.update(
        {
            "vehicle_id": payload.get("vehicle_id"),
            "distance_km": distance_km,
            "charging_kwh": charging_kwh,
            "solar_generation_kwh": solar_generation_kwh,
            "solar_self_consumption_kwh": solar_self_consumption_kwh,
            "solar_used_for_charging_kwh": solar_used_for_charging_kwh,
            "grid_charging_kwh": grid_charging_kwh,
            "baseline_emission_kgco2e": baseline_emission,
            "actual_emission_kgco2e": actual_emission,
            "solar_reduction_kgco2e": solar_reduction,
            "total_reduction_kgco2e": total_reduction,
            "total_reduction_tco2e": total_reduction / 1000,
            "diesel_emission_factor_per_km": diesel_factor,
            "grid_emission_factor": grid_factor,
            "formula": {
                "baseline_emission": "distance_km * diesel_emission_factor_per_km",
                "solar_used_for_charging": "min(solar_self_consumption_kwh, charging_kwh)",
                "grid_charging": "charging_kwh - solar_used_for_charging_kwh",
                "actual_emission": "grid_charging_kwh * grid_emission_factor",
                "total_reduction": "baseline_emission_kgCO2e - actual_emission_kgCO2e",
                "carbon_value": "(total_reduction_kgCO2e / 1000) * carbon_price_per_ton",
            },
        }
    )
    output["revenue"] = calculate_project_revenue(active_config)
    return output


def calculate_mobility_reduction(payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    source_type = payload["source_type"]
    mobility_key = MOBILITY_SOURCE_MAP.get(source_type)
    if not mobility_key:
        raise MobilitySolarCarbonError(f"UNSUPPORTED_MOBILITY_SOURCE_TYPE:{source_type}")

    if source_type == "EV_TAXI" and payload.get("charging_kwh") is not None:
        return calculate_ev_taxi_solar_reduction(payload, config)

    _required(payload, ["distance_km", "energy_consumed_kwh"])
    distance_km = float(payload["distance_km"])
    energy_consumed_kwh = float(payload["energy_consumed_kwh"])
    if distance_km < 0 or energy_consumed_kwh < 0:
        raise MobilitySolarCarbonError("NEGATIVE_INPUT_NOT_ALLOWED")

    source_config = config["mobility"][mobility_key]
    baseline_factor = float(source_config["baseline_vehicle"]["emission_factor"]["value"])
    grid_factor = float(config["global"]["grid_emission_factor"]["value"])
    baseline_emission = distance_km * baseline_factor
    actual_emission = energy_consumed_kwh * grid_factor
    reduction = baseline_emission - actual_emission

    output = _base_output(config, payload, reduction)
    output.update(
        {
            "baseline_emission_kgco2e": baseline_emission,
            "actual_emission_kgco2e": actual_emission,
            "distance_km": distance_km,
            "energy_consumed_kwh": energy_consumed_kwh,
            "charging_kwh": energy_consumed_kwh,
            "grid_charging_kwh": energy_consumed_kwh,
            "solar_used_for_charging_kwh": 0,
            "baseline_emission_factor": baseline_factor,
            "grid_emission_factor": grid_factor,
        }
    )
    output["revenue"] = calculate_project_revenue(config)
    return output


def calculate_solar_reduction(payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    _required(payload, ["solar_generation_kwh", "self_consumption_kwh", "grid_export_kwh"])
    solar_generation_kwh = float(payload["solar_generation_kwh"])
    self_consumption_kwh = float(payload["self_consumption_kwh"])
    grid_export_kwh = float(payload["grid_export_kwh"])
    if min(solar_generation_kwh, self_consumption_kwh, grid_export_kwh) < 0:
        raise MobilitySolarCarbonError("NEGATIVE_INPUT_NOT_ALLOWED")
    if self_consumption_kwh > solar_generation_kwh:
        raise MobilitySolarCarbonError("VALIDATION_FAILED:self_consumption_kwh <= solar_generation_kwh")
    if grid_export_kwh > solar_generation_kwh:
        raise MobilitySolarCarbonError("VALIDATION_FAILED:grid_export_kwh <= solar_generation_kwh")
    if self_consumption_kwh + grid_export_kwh > solar_generation_kwh:
        raise MobilitySolarCarbonError("VALIDATION_FAILED:self_consumption_kwh + grid_export_kwh <= solar_generation_kwh")

    grid_factor = float(config["global"]["grid_emission_factor"]["value"])
    reduction = self_consumption_kwh * grid_factor
    output = _base_output(config, payload, reduction)
    output.update(
        {
            "baseline_emission_kgco2e": reduction,
            "actual_emission_kgco2e": 0,
            "solar_generation_kwh": solar_generation_kwh,
            "self_consumption_kwh": self_consumption_kwh,
            "grid_export_kwh": grid_export_kwh,
            "grid_emission_factor": grid_factor,
        }
    )
    return output


def calculate_mobility_solar_carbon(payload: dict[str, Any]) -> dict[str, Any]:
    config = get_carbon_factor_config()
    source_type = str(payload.get("source_type", "")).upper()
    if not source_type:
        raise MobilitySolarCarbonError("REQUIRED_FIELD_MISSING:source_type")
    normalized_payload = {**payload, "source_type": source_type}

    if source_type in MOBILITY_SOURCE_MAP:
        return calculate_mobility_reduction(normalized_payload, config)
    if source_type == "SOLAR":
        return calculate_solar_reduction(normalized_payload, config)
    raise MobilitySolarCarbonError(f"UNSUPPORTED_SOURCE_TYPE:{source_type}")
