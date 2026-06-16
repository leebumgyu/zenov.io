from datetime import datetime
from typing import Optional

from ..config import settings
from ..api_models import TrustPacket

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
except ImportError:  # pragma: no cover - dependency optional in local doc-only mode
    InfluxDBClient = None
    Point = None
    WritePrecision = None


_client = None


def is_influx_configured() -> bool:
    return bool(settings.influxdb_url and settings.influxdb_token and InfluxDBClient)


def get_influx_client():
    global _client
    if not is_influx_configured():
        return None
    if _client is None:
        _client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
        )
    return _client


def write_sensor_reading(packet: TrustPacket, mrv_result: Optional[dict] = None, value_result: Optional[dict] = None) -> bool:
    client = get_influx_client()
    if client is None:
        return False

    timestamp = datetime.fromisoformat(packet.timestamp.replace("Z", "+00:00"))
    point = (
        Point("sensor_readings")
        .tag("site_id", packet.site_id)
        .tag("source_id", packet.source_id)
        .tag("asset_id", packet.asset_id or "")
        .tag("sensor_id", packet.sensor_id or "")
        .tag("packet_id", packet.packet_id)
        .time(timestamp, WritePrecision.NS)
    )

    for field in ["temperature_c", "humidity_pct", "co2_ppm", "ch4_ppm", "power_kwh", "equipment_status"]:
        if field in packet.payload and packet.payload[field] is not None:
            point = point.field(field, packet.payload[field])

    if mrv_result:
        point = point.tag("evidence_id", str(mrv_result.get("evidence_id") or ""))
        point = point.tag("mrv_id", str(mrv_result.get("mrv_id") or ""))
        point = point.field("co2e_kg", float(mrv_result["co2e_kg"]))
        point = point.field("co2e_ton", float(mrv_result["co2e_ton"]))
    if value_result:
        point = point.tag("value_id", str(value_result.get("value_id") or ""))
        point = point.field("estimated_carbon_value", float(value_result["estimated_value"]))

    write_api = client.write_api()
    write_api.write(bucket=settings.influxdb_bucket, org=settings.influxdb_org, record=point)
    return True


def influx_status() -> dict:
    if not is_influx_configured():
        return {"configured": False, "connected": False, "mode": "memory_fallback"}
    try:
        client = get_influx_client()
        health = client.health()
        return {
            "configured": True,
            "connected": getattr(health, "status", "") == "pass",
            "mode": "influxdb",
            "status": getattr(health, "status", "unknown"),
        }
    except Exception as exc:
        return {"configured": True, "connected": False, "mode": "memory_fallback", "error": str(exc)}
