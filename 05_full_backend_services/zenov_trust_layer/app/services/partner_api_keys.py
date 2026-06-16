from __future__ import annotations

import hmac
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from ..database.partner_crud import save_partner_api_key


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_key(raw_key: str) -> str:
    return sha256(raw_key.encode("utf-8")).hexdigest()


def create_partner_api_key(partner_id: str, label: str = "default") -> dict:
    raw_key = f"znv_{partner_id.lower()}_{uuid4().hex}"
    record = {
        "api_key_id": f"PAK-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
        "partner_id": partner_id,
        "label": label,
        "api_key_hash": _hash_key(raw_key),
        "status": "ACTIVE",
        "created_at": _now(),
        "last_used_at": None,
    }
    save_partner_api_key(record)
    return {**record, "api_key": raw_key}


def verify_partner_api_key(raw_key: str, api_key_hash: str) -> bool:
    return hmac.compare_digest(_hash_key(raw_key), api_key_hash)
