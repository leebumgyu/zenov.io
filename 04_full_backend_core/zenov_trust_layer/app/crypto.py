import hashlib
import hmac
import json
from typing import Any

from .config import settings


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def packet_hash_material(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": packet["source_id"],
        "site_id": packet["site_id"],
        "asset_id": packet.get("asset_id"),
        "sensor_id": packet.get("sensor_id"),
        "timestamp": packet["timestamp"],
        "sequence_no": packet["sequence_no"],
        "payload": packet["payload"],
    }


def compute_payload_hash(packet: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(packet_hash_material(packet)))


def sign_hash(payload_hash: str) -> str:
    digest = hmac.new(
        settings.hmac_secret.encode("utf-8"),
        payload_hash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"hmac-sha256:{digest}"


def verify_signature(payload_hash: str, signature: str) -> bool:
    expected = sign_hash(payload_hash)
    return hmac.compare_digest(expected, signature)
