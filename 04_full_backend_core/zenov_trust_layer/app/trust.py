from datetime import datetime, timezone

from .audit import record_audit
from .config import settings
from .crypto import compute_payload_hash, sign_hash
from .global_id import create_packet_id
from .api_models import RawSensorData, TrustPacket


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def create_trust_packet(raw_data: RawSensorData) -> TrustPacket:
    packet = {
        "packet_id": create_packet_id(settings.region),
        "source_id": raw_data.source_id,
        "site_id": raw_data.site_id,
        "asset_id": raw_data.asset_id,
        "sensor_id": raw_data.sensor_id,
        "timestamp": raw_data.timestamp or iso_now(),
        "sequence_no": raw_data.sequence_no,
        "payload": raw_data.payload,
        "payload_hash": "",
        "signature": "",
        "validation_status": "PENDING",
    }
    packet["payload_hash"] = compute_payload_hash(packet)
    packet["signature"] = sign_hash(packet["payload_hash"])
    trust_packet = TrustPacket(**packet)
    record_audit(trust_packet.packet_id, "PACKET_RECEIVED", {"source_id": trust_packet.source_id})
    return trust_packet
