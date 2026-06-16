from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ValidationStatus = Literal["PENDING", "VALIDATED", "REJECTED"]
DemoMode = Literal["NORMAL", "HASH_MISMATCH", "SIGNATURE_INVALID", "CARBON_VALUE_FAILED", "SENSOR_EXPIRED"]
CalibrationStatus = Literal["VALID", "WARNING", "EXPIRED", "FAILED"]


class RawSensorData(BaseModel):
    source_id: str
    site_id: str
    asset_id: Optional[str] = None
    sensor_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence_no: int = Field(ge=0)
    payload: dict[str, Any]


class GlobalIDRequest(BaseModel):
    object_type: str
    region: str
    domain: str


class GlobalIDResponse(BaseModel):
    global_id: str
    format: str = "TYPE-REGION-DOMAIN-YYYYMMDD-UUID"


class DemoGenerateRequest(BaseModel):
    mode: DemoMode = "NORMAL"
    calibration_status: CalibrationStatus = "VALID"
    packet_count: int = Field(default=1, ge=1, le=1000)


class CarbonFactorCalculationRequest(BaseModel):
    source_type: str
    payload: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class NavigationCarbonPredictionRequest(BaseModel):
    source_type: str = "EV_TAXI"
    vehicle_id: Optional[str] = None
    speed_series: list[float] = Field(default_factory=list)
    time_interval_seconds: float = Field(default=60, gt=0)
    gps_points: list[dict[str, Any]] = Field(default_factory=list)
    energy_consumed_kwh: Optional[float] = None
    solar_used_kwh: float = 0
    remaining_distance_km: Optional[float] = None

    class Config:
        extra = "allow"


class TaxiCsvImportRequest(BaseModel):
    csv_text: str
    import_batch_name: Optional[str] = None
    company_id: str = "ANSAN_TRANS"
    baseline_type: str = "lpg_taxi"


class TaxiBulkCsvImportRequest(BaseModel):
    csv_text: str
    job_name: Optional[str] = None
    source_filename: Optional[str] = None
    company_id: str = "ANSAN_TRANS"
    baseline_type: str = "lpg_taxi"
    generate_report: bool = True
    reporting_year: int = 2026


class PilotPortalCalculationRequest(BaseModel):
    partner_code: str = "ANSAN_TRANS"
    partner_login_code: Optional[str] = None
    referral_code: Optional[str] = None
    company_id: str = "ANSAN_TRANS"
    company_name: Optional[str] = "안산교통"
    vehicle_id: str
    driver_id: str
    operation_date: str
    distance_km: float = Field(gt=0)
    passenger_count: int = Field(ge=0)
    daily_revenue: float = Field(ge=0)
    energy_consumed_kwh: Optional[float] = Field(default=None, gt=0)
    baseline_type: str = "lpg_taxi"
    source_filename: str = "pilot-portal-manual-entry.csv"
    generate_report: bool = True
    reporting_year: int = 2026
    force_demo_unique: bool = True


class TrustPacket(BaseModel):
    packet_id: str
    source_id: str
    site_id: str
    asset_id: Optional[str] = None
    sensor_id: Optional[str] = None
    timestamp: str
    sequence_no: int
    payload: dict[str, Any]
    payload_hash: str
    signature: str
    validation_status: ValidationStatus = "PENDING"


class ValidationResult(BaseModel):
    packet_id: str
    validation_status: ValidationStatus
    reasons: list[str] = []
    validator_version: str


class IngestTraceabilityResponse(BaseModel):
    status: str
    packet_id: str
    evidence_id: Optional[str] = None
    mrv_id: Optional[str] = None
    value_id: Optional[str] = None
    asset_id: Optional[str] = None
    reason: Optional[str] = None
    traceability_status: str
    co2e_kg: Optional[float] = None
    co2e_ton: Optional[float] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    methodology_version: Optional[str] = None
    value_engine_version: Optional[str] = None


class RejectLog(BaseModel):
    packet_id: str
    source_id: str
    reason: list[str]
    raw_packet: dict[str, Any]
    rejected_at: datetime
    validator_version: str


class AuditEvent(BaseModel):
    packet_id: str
    event_type: str
    event_at: datetime
    detail: dict[str, Any] = {}


class StoredSensorPacket(BaseModel):
    packet: TrustPacket
    stored_at: datetime
