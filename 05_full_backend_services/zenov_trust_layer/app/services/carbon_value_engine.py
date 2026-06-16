from pathlib import Path
from typing import Any
from uuid import uuid4

from .config_loader import load_yaml_config


DEFAULT_PRICE_CONFIG = {
    "version_id": "CARBON_VALUE_ENGINE_V1.0",
    "currency": "KRW",
    "carbon_price_per_ton": 17000,
    "price_source": "PREMIUM_GS_SCENARIO",
    "price_date": "2026-06-19",
}


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "carbon-price-config.yaml"


class CarbonValueError(ValueError):
    pass


def get_carbon_price_config() -> dict[str, Any]:
    return load_yaml_config(CONFIG_PATH, DEFAULT_PRICE_CONFIG)


def calculate_carbon_value(mrv_result: dict[str, Any]) -> dict[str, Any]:
    config = get_carbon_price_config()
    carbon_price_per_ton = config.get("carbon_price_per_ton")
    currency = config.get("currency")
    price_source = config.get("price_source")
    price_date = config.get("price_date")
    value_engine_version = config.get("version_id")

    if not price_source or not price_date or carbon_price_per_ton is None:
        raise CarbonValueError("CARBON_PRICE_SOURCE_MISSING")
    if not value_engine_version:
        raise CarbonValueError("VALUE_ENGINE_VERSION_MISSING")

    co2e_ton = float(mrv_result["co2e_ton"])
    estimated_value = co2e_ton * float(carbon_price_per_ton)

    return {
        "value_id": f"VALUE-{uuid4().hex[:12].upper()}",
        "mrv_id": mrv_result["mrv_id"],
        "packet_id": mrv_result["packet_id"],
        "carbon_price_per_ton": float(carbon_price_per_ton),
        "currency": currency,
        "price_source": price_source,
        "price_date": price_date,
        "estimated_value": estimated_value,
        "value_engine_version": value_engine_version,
    }
