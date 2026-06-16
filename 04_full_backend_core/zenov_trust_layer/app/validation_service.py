from datetime import datetime

from .audit import record_audit
from .config import settings
from .crypto import compute_payload_hash, verify_signature
from .api_models import RejectLog, StoredSensorPacket, TrustPacket, ValidationResult
from .database.crud import (
    save_reject_record,
    save_trust_packet_record,
)
from .storage import packet_hash_index, save_packet, save_reject, sensor_packets, source_sequences


RANGE_RULES = {
    "ch4_ppm": (0, 10000),
    "co2_ppm": (0, 10000),
    "temperature_c": (-20, 80),
    "humidity_pct": (0, 100),
}


def validate_packet(packet: TrustPacket) -> ValidationResult:
    reasons: list[str] = []
    raw_packet = packet.model_dump()
    record_audit(packet.packet_id, "PACKET_RECEIVED", {"source_id": packet.source_id})
    save_trust_packet_record(packet)

    required_fields = ["packet_id", "source_id", "site_id", "timestamp", "sequence_no", "payload"]
    for field in required_fields:
        if raw_packet.get(field) in (None, "", {}):
            reasons.append(f"REQUIRED_FIELD_MISSING:{field}")

    try:
        datetime.fromisoformat(packet.timestamp.replace("Z", "+00:00"))
    except ValueError:
        reasons.append("TIMESTAMP_INVALID")

    if packet.sequence_no < 0:
        reasons.append("SEQUENCE_INVALID")

    last_sequence = source_sequences.get(packet.source_id)
    if last_sequence is not None and packet.sequence_no <= last_sequence:
        reasons.append("SEQUENCE_NOT_INCREASING")

    if packet.packet_id in sensor_packets or packet.payload_hash in packet_hash_index:
        reasons.append("DUPLICATE_PACKET")

    for key, (minimum, maximum) in RANGE_RULES.items():
        if key in packet.payload:
            value = packet.payload[key]
            if not isinstance(value, (int, float)):
                reasons.append(f"RANGE_TYPE_INVALID:{key}")
            elif value < minimum or value > maximum:
                reasons.append(f"RANGE_OUT_OF_BOUNDS:{key}")

    calibration_status = str(packet.payload.get("calibration_status", "VALID")).upper()
    if calibration_status == "EXPIRED":
        reasons.append("SENSOR_EXPIRED")
    elif calibration_status == "FAILED":
        reasons.append("SENSOR_FAILED")

    recalculated_hash = compute_payload_hash(raw_packet)
    if recalculated_hash != packet.payload_hash:
        reasons.append("HASH_RECALCULATION_FAILED")
    else:
        record_audit(packet.packet_id, "HASH_VERIFIED", {"payload_hash": packet.payload_hash})

    if not verify_signature(packet.payload_hash, packet.signature):
        reasons.append("SIGNATURE_INVALID")
    else:
        record_audit(packet.packet_id, "SIGNATURE_VERIFIED", {"signature_mode": settings.signature_mode})

    if reasons:
        packet.validation_status = "REJECTED"
        reject = RejectLog(
            packet_id=packet.packet_id,
            source_id=packet.source_id,
            reason=reasons,
            raw_packet=raw_packet,
            rejected_at=datetime.utcnow(),
            validator_version=settings.validator_version,
        )
        save_reject_record(reject)
        record_audit(packet.packet_id, "VALIDATION_FAILED", {"reasons": reasons})
        return ValidationResult(
            packet_id=packet.packet_id,
            validation_status="REJECTED",
            reasons=reasons,
            validator_version=settings.validator_version,
        )

    packet.validation_status = "VALIDATED"
    record_audit(packet.packet_id, "VALIDATION_SUCCESS", {})
    save_trust_packet_record(packet)
    save_packet(packet, StoredSensorPacket(packet=packet, stored_at=datetime.utcnow()))

    return ValidationResult(
        packet_id=packet.packet_id,
        validation_status="VALIDATED",
        reasons=[],
        validator_version=settings.validator_version,
    )
