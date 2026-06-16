from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from ..api_models import TrustPacket
from ..crypto import canonical_json, compute_payload_hash, sha256_hex, verify_signature
from ..models.evidence import DigitalEvidence, EvidenceArtifact, EvidenceBundle, EvidenceSensorMapping, IntegrityReport
from ..database.evidence_crud import save_evidence_bundle

EVIDENCE_ENGINE_VERSION = "DIGITAL_EVIDENCE_ENGINE_V1.0"


def _new_id(prefix: str) -> str:
    issued_at = datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}-KR-{issued_at}-{uuid4().hex[:8].upper()}"


def _source_type(packet: TrustPacket) -> str:
    payload_source = packet.payload.get("source_type")
    if payload_source:
        return str(payload_source).upper()
    if packet.sensor_id and "CH4" in packet.sensor_id.upper():
        return "SENSOR_CH4"
    return "SENSOR_TELEMETRY"


def _calculate_trust_score(packet: TrustPacket, hash_verified: bool, signature_verified: bool, canonical_verified: bool) -> float:
    score = 100.0
    if not hash_verified:
        score -= 45.0
    if not signature_verified:
        score -= 35.0
    if not canonical_verified:
        score -= 10.0

    calibration_status = str(packet.payload.get("calibration_status", "VALID")).upper()
    if calibration_status == "WARNING":
        score -= 8.0
    elif calibration_status == "EXPIRED":
        score -= 50.0
    elif calibration_status == "FAILED":
        score -= 70.0
    return max(0.0, round(score, 2))


def create_evidence(packet: TrustPacket, verifier_name: str = "ZENOV_TRUST_LAYER") -> EvidenceBundle:
    hash_verified = compute_payload_hash(packet.model_dump()) == packet.payload_hash
    signature_verified = verify_signature(packet.payload_hash, packet.signature)
    canonical_verified = bool(canonical_json(packet.model_dump()))
    trust_score = _calculate_trust_score(packet, hash_verified, signature_verified, canonical_verified)

    evidence_id = _new_id("EVD")
    integrity_report_id = _new_id("IRP")
    mapping_id = _new_id("ESM")
    now = datetime.now(timezone.utc)
    evidence_hash = sha256_hex(
        canonical_json(
            {
                "packet_id": packet.packet_id,
                "source_id": packet.source_id,
                "site_id": packet.site_id,
                "sensor_id": packet.sensor_id,
                "payload_hash": packet.payload_hash,
                "signature": packet.signature,
                "timestamp": packet.timestamp,
                "sequence_no": packet.sequence_no,
                "engine_version": EVIDENCE_ENGINE_VERSION,
            }
        )
    )
    signature_hash = sha256_hex(packet.signature)
    integrity_status = "VERIFIED" if hash_verified and signature_verified and canonical_verified else "FAILED"

    bundle = EvidenceBundle(
        evidence=DigitalEvidence(
            evidence_id=evidence_id,
            packet_id=packet.packet_id,
            evidence_type="TRUST_PACKET_EVIDENCE",
            source_type=_source_type(packet),
            trust_score=trust_score,
            evidence_hash=evidence_hash,
            signature_hash=signature_hash,
            created_at=now,
            status="ACTIVE" if integrity_status == "VERIFIED" else "FAILED",
        ),
        integrity_report=IntegrityReport(
            integrity_report_id=integrity_report_id,
            evidence_id=evidence_id,
            hash_verified=hash_verified,
            signature_verified=signature_verified,
            canonical_verified=canonical_verified,
            verifier_name=verifier_name,
            verification_time=now,
            status=integrity_status,
        ),
        sensor_mapping=EvidenceSensorMapping(
            mapping_id=mapping_id,
            evidence_id=evidence_id,
            sensor_id=packet.sensor_id,
            gateway_id=packet.payload.get("gateway_id"),
            calibration_id=packet.payload.get("calibration_id"),
        ),
        metadata={"engine_version": EVIDENCE_ENGINE_VERSION},
    )
    save_evidence_bundle(bundle)
    return bundle


def attach_artifact(evidence_id: str, file_path: str, artifact_type: str) -> EvidenceArtifact:
    path = Path(file_path)
    content = path.read_bytes()
    now = datetime.now(timezone.utc)
    return EvidenceArtifact(
        artifact_id=_new_id("ART"),
        evidence_id=evidence_id,
        artifact_type=artifact_type,
        file_path=str(path),
        file_hash=sha256_hex(content.hex()),
        file_size=len(content),
        created_at=now,
    )


def verify_evidence(bundle: EvidenceBundle) -> dict[str, object]:
    report = bundle.integrity_report
    verified = report.hash_verified and report.signature_verified and report.canonical_verified
    return {
        "evidence_id": bundle.evidence.evidence_id,
        "verified": verified,
        "trust_score": bundle.evidence.trust_score,
        "integrity_report_id": report.integrity_report_id,
        "status": report.status,
    }


def generate_integrity_report(evidence_id: str, output_path: Optional[str] = None) -> dict[str, str]:
    report_path = output_path or f"integrity-report-{evidence_id}.pdf"
    return {
        "evidence_id": evidence_id,
        "report_path": report_path,
        "status": "REPORT_TEMPLATE_READY",
    }

