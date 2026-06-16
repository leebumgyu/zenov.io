from pathlib import Path
from typing import Any
from uuid import uuid4

from ..crypto import canonical_json, sha256_hex
from .config_loader import load_yaml_config


DEFAULT_MRV_CONFIG = {
    "version_id": "MRV_ENGINE_V1.0",
    "methodology_version": "METHANE_CO2E_POC_METHODOLOGY_V1.0",
    "emission_factor_version": "EMISSION_FACTOR_KR_POC_2026",
    "calculation_version": "MRV_CALC_POC_V1.0",
    "factors": {
        "ch4_gwp100": 28.0,
        "co2_factor": 1.0,
        "ppm_to_kg_factor": 0.000001,
    },
}


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "mrv-engine-config.yaml"


class MRVCalculationError(ValueError):
    pass


def get_mrv_config() -> dict[str, Any]:
    return load_yaml_config(CONFIG_PATH, DEFAULT_MRV_CONFIG)


def calculate_mrv(payload: dict[str, Any], packet_id: str, source_id: str) -> dict[str, Any]:
    config = get_mrv_config()
    methodology_version = config.get("methodology_version")
    emission_factor_version = config.get("emission_factor_version")
    calculation_version = config.get("calculation_version")

    if not methodology_version or not emission_factor_version or not calculation_version:
        raise MRVCalculationError("MRV_CONFIG_VERSION_MISSING")

    ch4_ppm = float(payload.get("ch4_ppm", 0) or 0)
    co2_ppm = float(payload.get("co2_ppm", 0) or 0)
    flow_m3h = float(payload.get("flow_m3h", 1) or 1)
    power_kwh = float(payload.get("power_kwh", 0) or 0)

    factors = config.get("factors", {})
    ch4_gwp100 = float(factors.get("ch4_gwp100", 28.0))
    co2_factor = float(factors.get("co2_factor", 1.0))
    ppm_to_kg_factor = float(factors.get("ppm_to_kg_factor", 0.000001))

    co2e_kg = ((ch4_ppm * ch4_gwp100) + (co2_ppm * co2_factor)) * ppm_to_kg_factor * flow_m3h
    co2e_ton = co2e_kg / 1000

    material = {
        "packet_id": packet_id,
        "source_id": source_id,
        "ch4_ppm": ch4_ppm,
        "co2_ppm": co2_ppm,
        "flow_m3h": flow_m3h,
        "power_kwh": power_kwh,
        "co2e_kg": co2e_kg,
        "methodology_version": methodology_version,
        "emission_factor_version": emission_factor_version,
        "calculation_version": calculation_version,
    }

    return {
        "mrv_id": f"MRV-{uuid4().hex[:12].upper()}",
        "packet_id": packet_id,
        "source_id": source_id,
        "co2e_kg": co2e_kg,
        "co2e_ton": co2e_ton,
        "methodology_version": methodology_version,
        "emission_factor_version": emission_factor_version,
        "calculation_version": calculation_version,
        "calculation_hash": sha256_hex(canonical_json(material)),
    }
