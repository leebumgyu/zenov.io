from __future__ import annotations

from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Any

from .mobility_solar_carbon_engine import (
    MOBILITY_SOURCE_MAP,
    METHODOLOGY_VERSION,
    MobilitySolarCarbonError,
    calculate_mobility_solar_carbon,
    get_carbon_factor_config,
)


EARTH_RADIUS_KM = 6371.0088


def _parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MobilitySolarCarbonError(f"INVALID_TIMESTAMP:{value}") from exc


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    rlat1 = radians(lat1)
    rlat2 = radians(lat2)
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def _distance_from_speed_series(speed_series: list[float], time_interval_seconds: float) -> dict[str, Any]:
    if not speed_series:
        raise MobilitySolarCarbonError("REQUIRED_FIELD_MISSING:speed_series")
    if time_interval_seconds <= 0:
        raise MobilitySolarCarbonError("INVALID_TIME_INTERVAL")
    interval_hours = time_interval_seconds / 3600
    distance_km = sum(float(speed) * interval_hours for speed in speed_series)
    average_speed_kmh = sum(float(speed) for speed in speed_series) / len(speed_series)
    return {
        "distance_km": distance_km,
        "average_speed_kmh": average_speed_kmh,
        "sample_count": len(speed_series),
        "calculation_pattern": "SPEED_INTEGRATION",
    }


def _distance_from_gps_points(gps_points: list[dict[str, Any]]) -> dict[str, Any]:
    if len(gps_points) < 2:
        raise MobilitySolarCarbonError("REQUIRED_FIELD_MISSING:gps_points>=2")

    total_distance_km = 0.0
    passenger_distance_km = 0.0
    empty_distance_km = 0.0
    total_seconds = 0.0

    ordered_points = sorted(gps_points, key=lambda item: str(item.get("timestamp", "")))
    previous = ordered_points[0]
    previous_time = _parse_timestamp(str(previous["timestamp"]))

    for current in ordered_points[1:]:
        current_time = _parse_timestamp(str(current["timestamp"]))
        seconds = (current_time - previous_time).total_seconds()
        if seconds < 0:
            raise MobilitySolarCarbonError("GPS_TIMESTAMP_NOT_MONOTONIC")
        segment_km = _haversine_km(
            float(previous["lat"]),
            float(previous["lon"]),
            float(current["lat"]),
            float(current["lon"]),
        )
        total_distance_km += segment_km
        total_seconds += seconds
        if bool(current.get("occupied", previous.get("occupied", False))):
            passenger_distance_km += segment_km
        else:
            empty_distance_km += segment_km
        previous = current
        previous_time = current_time

    average_speed_kmh = (total_distance_km / (total_seconds / 3600)) if total_seconds else 0
    return {
        "distance_km": total_distance_km,
        "passenger_distance_km": passenger_distance_km,
        "empty_distance_km": empty_distance_km,
        "average_speed_kmh": average_speed_kmh,
        "sample_count": len(ordered_points),
        "calculation_pattern": "GPS_DIFFERENTIATION_AND_DISTANCE_INTEGRATION",
    }


def predict_navigation_carbon_reduction(payload: dict[str, Any]) -> dict[str, Any]:
    source_type = str(payload.get("source_type", "EV_TAXI")).upper()
    if source_type not in MOBILITY_SOURCE_MAP:
        raise MobilitySolarCarbonError(f"UNSUPPORTED_MOBILITY_SOURCE_TYPE:{source_type}")

    if payload.get("gps_points"):
        movement = _distance_from_gps_points(payload["gps_points"])
    else:
        movement = _distance_from_speed_series(
            [float(speed) for speed in payload.get("speed_series", [])],
            float(payload.get("time_interval_seconds", 60)),
        )

    config = get_carbon_factor_config()
    mobility_key = MOBILITY_SOURCE_MAP[source_type]
    energy_consumed_kwh = payload.get("energy_consumed_kwh")
    if energy_consumed_kwh is None:
        default_energy = (
            config.get("mobility", {})
            .get(mobility_key, {})
            .get("default_energy_kwh_per_km", {})
            .get("value")
        )
        if default_energy is None:
            raise MobilitySolarCarbonError("REQUIRED_FIELD_MISSING:energy_consumed_kwh")
        energy_consumed_kwh = movement["distance_km"] * float(default_energy)

    mobility_payload = {
        **payload,
        "source_type": source_type,
        "distance_km": movement["distance_km"],
        "energy_consumed_kwh": float(energy_consumed_kwh),
    }
    mobility_result = calculate_mobility_solar_carbon(mobility_payload)

    solar_used_kwh = float(payload.get("solar_used_kwh", 0) or 0)
    grid_factor = float(config["global"]["grid_emission_factor"]["value"])
    solar_reduction_kgco2e = solar_used_kwh * grid_factor
    total_reduction_kgco2e = mobility_result["reduction_kgco2e"] + solar_reduction_kgco2e
    total_reduction_tco2e = total_reduction_kgco2e / 1000
    carbon_price = float(config["global"]["carbon_price"]["value"])

    average_speed_kmh = movement["average_speed_kmh"]
    remaining_distance_km = payload.get("remaining_distance_km")
    eta_minutes = None
    if remaining_distance_km is not None and average_speed_kmh > 0:
        eta_minutes = (float(remaining_distance_km) / average_speed_kmh) * 60

    return {
        "engine": "NAVIGATION_BASED_CARBON_MRV_ENGINE",
        "pattern": "Mobility Integral Carbon MRV Pattern",
        "methodology_version": METHODOLOGY_VERSION,
        "factor_config_version": mobility_result["factor_config_version"],
        "source_type": source_type,
        "vehicle_id": payload.get("vehicle_id"),
        "distance_km": movement["distance_km"],
        "passenger_distance_km": movement.get("passenger_distance_km"),
        "empty_distance_km": movement.get("empty_distance_km"),
        "average_speed_kmh": average_speed_kmh,
        "eta_minutes": eta_minutes,
        "energy_consumed_kwh": float(energy_consumed_kwh),
        "baseline_emission_kgco2e": mobility_result["baseline_emission_kgco2e"],
        "actual_emission_kgco2e": mobility_result["actual_emission_kgco2e"],
        "mobility_reduction_kgco2e": mobility_result["reduction_kgco2e"],
        "solar_used_kwh": solar_used_kwh,
        "solar_reduction_kgco2e": solar_reduction_kgco2e,
        "total_reduction_kgco2e": total_reduction_kgco2e,
        "total_reduction_tco2e": total_reduction_tco2e,
        "estimated_value": total_reduction_tco2e * carbon_price,
        "currency": config.get("currency", "KRW"),
        "carbon_price_per_ton": carbon_price,
        "price_source": config["global"]["carbon_price"].get("source"),
        "price_date": config["global"]["carbon_price"].get("price_date"),
        "movement_calculation": movement["calculation_pattern"],
        "sample_count": movement["sample_count"],
    }
