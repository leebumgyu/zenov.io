from typing import Any, Optional

from ..models.evidence import EvidenceBundle
from ..storage import (
    digital_evidence,
    evidence_by_packet_id,
    integrity_report_by_evidence_id,
    integrity_reports,
    save_evidence_memory,
)
from .models import DigitalEvidenceModel, EvidenceSensorMappingModel, IntegrityReportModel
from .postgres import session_scope


def save_evidence_bundle(bundle: EvidenceBundle) -> bool:
    data = bundle.model_dump()
    with session_scope() as session:
        if session is None:
            save_evidence_memory(data)
            return False

        evidence = bundle.evidence
        integrity_report = bundle.integrity_report
        sensor_mapping = bundle.sensor_mapping
        session.merge(
            DigitalEvidenceModel(
                evidence_id=evidence.evidence_id,
                packet_id=evidence.packet_id,
                evidence_type=evidence.evidence_type,
                source_type=evidence.source_type,
                trust_score=evidence.trust_score,
                evidence_hash=evidence.evidence_hash,
                signature_hash=evidence.signature_hash,
                created_at=evidence.created_at,
                status=evidence.status,
            )
        )
        session.merge(
            IntegrityReportModel(
                integrity_report_id=integrity_report.integrity_report_id,
                evidence_id=integrity_report.evidence_id,
                hash_verified=integrity_report.hash_verified,
                signature_verified=integrity_report.signature_verified,
                canonical_verified=integrity_report.canonical_verified,
                verifier_name=integrity_report.verifier_name,
                verification_time=integrity_report.verification_time,
                status=integrity_report.status,
            )
        )
        session.merge(
            EvidenceSensorMappingModel(
                mapping_id=sensor_mapping.mapping_id,
                evidence_id=sensor_mapping.evidence_id,
                sensor_id=sensor_mapping.sensor_id,
                gateway_id=sensor_mapping.gateway_id,
                calibration_id=sensor_mapping.calibration_id,
            )
        )
        return True


def get_evidence_by_packet(packet_id: str) -> Optional[dict[str, Any]]:
    with session_scope() as session:
        if session is not None:
            row = session.query(DigitalEvidenceModel).filter(DigitalEvidenceModel.packet_id == packet_id).first()
            if not row:
                return None
            report = (
                session.query(IntegrityReportModel)
                .filter(IntegrityReportModel.evidence_id == row.evidence_id)
                .first()
            )
            return {
                "evidence_id": row.evidence_id,
                "packet_id": row.packet_id,
                "evidence_type": row.evidence_type,
                "source_type": row.source_type,
                "trust_score": row.trust_score,
                "evidence_hash": row.evidence_hash,
                "signature_hash": row.signature_hash,
                "created_at": row.created_at,
                "status": row.status,
                "integrity_report": {
                    "integrity_report_id": report.integrity_report_id,
                    "hash_verified": report.hash_verified,
                    "signature_verified": report.signature_verified,
                    "canonical_verified": report.canonical_verified,
                    "verifier_name": report.verifier_name,
                    "verification_time": report.verification_time,
                    "status": report.status,
                } if report else None,
            }

    evidence_id = evidence_by_packet_id.get(packet_id)
    if not evidence_id:
        return None
    evidence = digital_evidence.get(evidence_id)
    report_id = integrity_report_by_evidence_id.get(evidence_id)
    report = integrity_reports.get(report_id) if report_id else None
    return {**evidence, "integrity_report": report} if evidence else None

