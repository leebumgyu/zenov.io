from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from .api_models import ValidationStatus


class GlobalIDRecord(BaseModel):
    zenov_id: str
    entity_type: str
    region: str
    domain: str
    created_at: datetime
    metadata: dict[str, Any] = {}


class TrustPacketRecord(BaseModel):
    packet_id: str
    source_id: str
    site_id: str
    asset_id: Optional[str] = None
    sensor_id: Optional[str] = None
    timestamp: datetime
    sequence_no: int
    payload_hash: str
    signature: str
    validation_status: ValidationStatus
    created_at: datetime


class AuditLogRecord(BaseModel):
    audit_id: int
    packet_id: str
    event_type: str
    event_status: str = "INFO"
    message: Optional[str] = None
    actor: str = "system"
    created_at: datetime


class RejectLogRecord(BaseModel):
    reject_id: int
    packet_id: str
    source_id: str
    reason_code: str
    reason_message: Optional[str] = None
    raw_packet: dict[str, Any]
    validator_version: str
    rejected_at: datetime


class SensorReadingPoint(BaseModel):
    measurement: str = "sensor_readings"
    site_id: str
    source_id: str
    packet_id: str
    timestamp: datetime
    asset_id: Optional[str] = None
    sensor_id: Optional[str] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    co2_ppm: Optional[float] = None
    ch4_ppm: Optional[float] = None
    power_kwh: Optional[float] = None
    equipment_status: Optional[str] = None
    co2e_kg: Optional[float] = None
    co2e_ton: Optional[float] = None
    estimated_carbon_value: Optional[float] = None


class MRVResultRecord(BaseModel):
    mrv_id: str
    packet_id: str
    source_id: str
    co2e_kg: float
    co2e_ton: float
    methodology_version: str
    emission_factor_version: str
    calculation_hash: str
    created_at: datetime


class CarbonValueResultRecord(BaseModel):
    value_id: str
    mrv_id: str
    packet_id: str
    carbon_price_per_ton: float
    currency: str
    price_source: str
    price_date: datetime
    estimated_value: float
    value_engine_version: str
    created_at: datetime


class TraceabilityView(BaseModel):
    packet: TrustPacketRecord
    audit_logs: list[AuditLogRecord]
    reject_logs: list[RejectLogRecord] = []
    sensor_readings: list[SensorReadingPoint] = []
    mrv_results: list[MRVResultRecord] = []
    carbon_value_results: list[CarbonValueResultRecord] = []
