from __future__ import annotations

from typing import Any

from ..database.partner_crud import find_partner_mapping


STANDARD_MODEL_FIELDS = {
    "taxi_daily_operation": {
        "vehicle_id",
        "operation_date",
        "distance_km",
        "passenger_count",
        "daily_revenue",
        "driver_id",
        "energy_consumed_kwh",
    },
    "vehicle_operation_log": {
        "vehicle_id",
        "operation_date",
        "distance_km",
        "driving_time_min",
        "idle_time_min",
        "driver_id",
    },
    "mobility_tracking_log": {
        "vehicle_id",
        "timestamp",
        "latitude",
        "longitude",
        "speed_kmh",
    },
    "charging_session": {
        "charger_id",
        "vehicle_id",
        "charging_start_time",
        "charging_end_time",
        "charged_kwh",
        "solar_used_kwh",
        "grid_used_kwh",
    },
}


DEFAULT_MAPPING_TEMPLATES = {
    "TMONEY_CSV": {
        "source_type": "TMONEY_CSV",
        "standard_model": "taxi_daily_operation",
        "field_map": {
            "차량번호": "vehicle_id",
            "운행일": "operation_date",
            "주행거리": "distance_km",
            "승객수": "passenger_count",
            "매출": "daily_revenue",
            "기사ID": "driver_id",
            "전기사용량": "energy_consumed_kwh",
        },
    },
    "DTG": {
        "source_type": "DTG",
        "standard_model": "vehicle_operation_log",
        "field_map": {
            "car_no": "vehicle_id",
            "date": "operation_date",
            "distance": "distance_km",
            "drive_min": "driving_time_min",
            "idle_min": "idle_time_min",
            "driver": "driver_id",
        },
    },
    "GPS": {
        "source_type": "GPS",
        "standard_model": "mobility_tracking_log",
        "field_map": {
            "car_no": "vehicle_id",
            "ts": "timestamp",
            "lat": "latitude",
            "lng": "longitude",
            "speed": "speed_kmh",
        },
    },
    "CHARGER_API": {
        "source_type": "CHARGER_API",
        "standard_model": "charging_session",
        "field_map": {
            "chargerId": "charger_id",
            "vehicleId": "vehicle_id",
            "startedAt": "charging_start_time",
            "endedAt": "charging_end_time",
            "kwh": "charged_kwh",
            "solarKwh": "solar_used_kwh",
            "gridKwh": "grid_used_kwh",
        },
    },
}


def default_mapping_for(source_type: str) -> dict[str, Any]:
    template = DEFAULT_MAPPING_TEMPLATES.get(source_type)
    if template:
        return template
    return {
        "source_type": source_type,
        "standard_model": "taxi_daily_operation",
        "field_map": {},
    }


def validate_mapping(standard_model: str, field_map: dict[str, str]) -> dict[str, Any]:
    allowed_fields = STANDARD_MODEL_FIELDS.get(standard_model, set())
    mapped_fields = set(field_map.values())
    unknown = sorted(mapped_fields - allowed_fields)
    missing = sorted(
        field for field in allowed_fields
        if field in {"vehicle_id", "operation_date", "distance_km"} and field not in mapped_fields
    )
    status = "MAPPING_OK" if not unknown and not missing else "MAPPING_WARNING"
    return {
        "status": status,
        "standard_model": standard_model,
        "unknown_target_fields": unknown,
        "missing_required_fields": missing,
    }


def map_external_record(partner_id: str, source_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    mapping = find_partner_mapping(partner_id, source_type)
    if not mapping:
        raise ValueError(f"MAPPING_NOT_FOUND:{partner_id}:{source_type}")
    field_map = mapping.get("field_map", {})
    normalized = {}
    mapping_errors = []
    for source_field, value in payload.items():
        target_field = field_map.get(source_field)
        if target_field:
            normalized[target_field] = value
    for required in ("vehicle_id", "operation_date", "distance_km"):
        if mapping.get("standard_model") == "taxi_daily_operation" and normalized.get(required) in (None, ""):
            mapping_errors.append(f"MISSING_REQUIRED_FIELD:{required}")
    return {
        "partner_id": partner_id,
        "source_type": source_type,
        "standard_model": mapping.get("standard_model"),
        "normalized_payload": normalized,
        "mapping_status": "MAPPING_OK" if not mapping_errors else "MAPPING_FAILED",
        "mapping_errors": mapping_errors,
        "mapping_id": mapping.get("mapping_id"),
    }
