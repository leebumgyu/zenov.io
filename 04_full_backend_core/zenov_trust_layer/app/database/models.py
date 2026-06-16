from datetime import datetime

try:
    from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Integer, JSON, String, Text
    from sqlalchemy.orm import declarative_base
except ImportError:  # pragma: no cover
    BigInteger = Boolean = Column = DateTime = Float = Integer = JSON = String = Text = None

    class _Base:
        metadata = None

    def declarative_base():
        return _Base


Base = declarative_base()


class GlobalIDModel(Base):
    __tablename__ = "global_ids"

    zenov_id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False)
    region = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)


class TrustPacketModel(Base):
    __tablename__ = "trust_packets"

    packet_id = Column(String, primary_key=True)
    source_id = Column(String, nullable=False)
    site_id = Column(String, nullable=False)
    asset_id = Column(String)
    sensor_id = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    sequence_no = Column(BigInteger, nullable=False)
    payload_hash = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    raw_packet = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    packet_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_status = Column(String, nullable=False, default="INFO")
    evidence_id = Column(String)
    mrv_id = Column(String)
    value_id = Column(String)
    asset_id = Column(String)
    message = Column(Text)
    actor = Column(String, nullable=False, default="system")
    detail = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RejectLogModel(Base):
    __tablename__ = "reject_logs"

    reject_id = Column(Integer, primary_key=True, autoincrement=True)
    packet_id = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    reason_message = Column(Text)
    raw_packet = Column(JSON, nullable=False)
    validator_version = Column(String, nullable=False)
    rejected_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class MRVResultModel(Base):
    __tablename__ = "mrv_results"

    mrv_id = Column(String, primary_key=True)
    packet_id = Column(String, nullable=False)
    evidence_id = Column(String)
    source_id = Column(String, nullable=False)
    co2e_kg = Column(Float, nullable=False)
    co2e_ton = Column(Float, nullable=False)
    methodology_version = Column(String, nullable=False)
    emission_factor_version = Column(String, nullable=False)
    calculation_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="SUCCESS")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class CarbonValueResultModel(Base):
    __tablename__ = "carbon_value_results"

    value_id = Column(String, primary_key=True)
    mrv_id = Column(String, nullable=False)
    packet_id = Column(String, nullable=False)
    carbon_price_per_ton = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    price_source = Column(String, nullable=False)
    price_date = Column(DateTime(timezone=True), nullable=False)
    estimated_value = Column(Float, nullable=False)
    value_engine_version = Column(String, nullable=False)
    status = Column(String, nullable=False, default="SUCCESS")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class DigitalEvidenceModel(Base):
    __tablename__ = "digital_evidence"

    evidence_id = Column(String, primary_key=True)
    packet_id = Column(String, nullable=False)
    evidence_type = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    trust_score = Column(Float)
    evidence_hash = Column(String, nullable=False)
    signature_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="ACTIVE")


class EvidenceArtifactModel(Base):
    __tablename__ = "evidence_artifacts"

    artifact_id = Column(String, primary_key=True)
    evidence_id = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False)
    file_path = Column(Text)
    file_hash = Column(String, nullable=False)
    file_size = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class IntegrityReportModel(Base):
    __tablename__ = "integrity_reports"

    integrity_report_id = Column(String, primary_key=True)
    evidence_id = Column(String, nullable=False)
    hash_verified = Column(Boolean, nullable=False, default=False)
    signature_verified = Column(Boolean, nullable=False, default=False)
    canonical_verified = Column(Boolean, nullable=False, default=False)
    verifier_name = Column(String, nullable=False, default="ZENOV_TRUST_LAYER")
    verification_time = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="PENDING")


class CalibrationRecordModel(Base):
    __tablename__ = "calibration_records"

    calibration_id = Column(String, primary_key=True)
    sensor_id = Column(String, nullable=False)
    certificate_number = Column(String)
    calibration_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    calibration_file = Column(Text)
    status = Column(String, nullable=False, default="UNKNOWN")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class EvidenceSensorMappingModel(Base):
    __tablename__ = "evidence_sensor_mapping"

    mapping_id = Column(String, primary_key=True)
    evidence_id = Column(String, nullable=False)
    sensor_id = Column(String)
    gateway_id = Column(String)
    calibration_id = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
