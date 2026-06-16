from datetime import datetime
from typing import Any, Optional

from .api_models import AuditEvent
from .storage import save_audit


def record_audit(packet_id: str, event_type: str, detail: Optional[dict[str, Any]] = None) -> None:
    save_audit(
        AuditEvent(
            packet_id=packet_id,
            event_type=event_type,
            event_at=datetime.utcnow(),
            detail=detail or {},
        )
    )
