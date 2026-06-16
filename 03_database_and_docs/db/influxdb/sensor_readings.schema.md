# InfluxDB Measurement: sensor_readings

## Purpose

Store validated sensor time-series values.

Only packets with `validation_status = VALIDATED` should be written to this measurement.

---

## Measurement

```text
sensor_readings
```

---

## Tags

- `site_id`
- `source_id`
- `asset_id`
- `sensor_id`
- `packet_id`

---

## Fields

- `temperature_c`
- `humidity_pct`
- `co2_ppm`
- `ch4_ppm`
- `power_kwh`
- `equipment_status`
- `co2e_kg`
- `co2e_ton`
- `estimated_carbon_value`

---

## Timestamp

Use Trust Packet `timestamp`.

---

## Example Line Protocol

```text
sensor_readings,site_id=SITE-KR-PLANT-001,source_id=SENSOR-KR-CH4-001,asset_id=AST-KR-FACTORY-001,sensor_id=SENSOR-KR-CH4-001,packet_id=PKT-KR-20260619-000001 ch4_ppm=145,co2_ppm=850,temperature_c=27.5 1781840400000000000
```

---

## Linkage Rule

`packet_id` must be stored as a tag so that each InfluxDB reading can be traced back to:

- PostgreSQL `trust_packets`
- PostgreSQL `audit_logs`
- PostgreSQL `reject_logs` if validation failed before time-series insertion

---

## Write Rule

Rejected packets must not be written to InfluxDB.

Rejected packet raw data must be preserved in PostgreSQL `reject_logs`.
