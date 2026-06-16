# ZENOV MOBILITY CARBON MRV ENGINE

## Technology

Navigation-Based Carbon MRV Engine

## Objective

Zenov calculates electric mobility carbon reduction from navigation, GPS, speed, charging, battery, and solar charging data.

The engine converts verified mobility movement into:

- distance_km
- baseline_emission_kgco2e
- actual_emission_kgco2e
- mobility_reduction_kgco2e
- solar_reduction_kgco2e
- total_reduction_tco2e
- estimated carbon value

## Calculation Pattern

1. GPS position changes are interpreted as movement.
2. Position change over time derives speed.
3. Speed over time is integrated into distance.
4. Distance is multiplied by the baseline emission factor.
5. Electric energy use is multiplied by the grid emission factor.
6. The difference becomes carbon reduction.

```text
GPS / Speed / Battery / Charging / Solar
↓
Trust Layer
↓
Validation Engine
↓
Navigation-Based Carbon MRV Engine
↓
Carbon Value Engine
↓
Carbon Asset
```

## API

```text
POST /api/v1/navigation-carbon/predict
```

## Speed-Series Input

```json
{
  "source_type": "EV_TAXI",
  "vehicle_id": "VEH-KR-TAXI-001",
  "speed_series": [35, 42, 38, 44, 40],
  "time_interval_seconds": 60,
  "energy_consumed_kwh": 2.8,
  "solar_used_kwh": 1.2,
  "remaining_distance_km": 20
}
```

## GPS Input

```json
{
  "source_type": "EV_TAXI",
  "vehicle_id": "VEH-KR-TAXI-001",
  "gps_points": [
    {"lat": 37.321, "lon": 126.830, "timestamp": "2026-06-19T10:00:00+09:00", "occupied": true},
    {"lat": 37.331, "lon": 126.840, "timestamp": "2026-06-19T10:05:00+09:00", "occupied": true}
  ],
  "energy_consumed_kwh": 0.5
}
```

## Rule

Emission factors, grid factors, carbon prices, and methodology versions must be loaded from `carbon-factor-config.yaml`.

Do not hardcode official calculation factors in application code.
