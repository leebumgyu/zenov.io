from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DigitalEvidence(BaseModel):
    evidence_id: str
    packet_id: str
    evidence_type: str
    source_type: str
    trust_score: float
    evidence_hash: str
    signature_hash: str
    created_at: datetime
    status: str = "ACTIVE"


class EvidenceArtifact(BaseModel):
    artifact_id: str
    evidence_id: str
    artifact_type: str
    file_path: Optional[str] = None
    file_hash: str
    file_size: Optional[int] = None
    created_at: datetime


class IntegrityReport(BaseModel):
    integrity_report_id: str
    evidence_id: str
    hash_verified: bool
    signature_verified: bool
    canonical_verified: bool
    verifier_name: str
    verification_time: datetime
    status: str


class CalibrationRecord(BaseModel):
    calibration_id: str
    sensor_id: str
    certificate_number: Optional[str] = None
    calibration_date: Optional[str] = None
    expiration_date: Optional[str] = None
    calibration_file: Optional[str] = None
    status: str = "UNKNOWN"


class EvidenceSensorMapping(BaseModel):
    mapping_id: str
    evidence_id: str
    sensor_id: Optional[str] = None
    gateway_id: Optional[str] = None
    calibration_id: Optional[str] = None


class EvidenceBundle(BaseModel):
    evidence: DigitalEvidence
    integrity_report: IntegrityReport
    sensor_mapping: EvidenceSensorMapping
    artifacts: list[EvidenceArtifact] = []
    metadata: dict[str, Any] = {}

