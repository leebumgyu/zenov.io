from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..database.crud import get_full_trace_detail
from ..storage import (
    digital_evidence,
    evidence_by_packet_id,
    mrv_verification_records,
    save_evidence_explanation_memory,
    taxi_mrv_by_packet_id,
    taxi_mrv_results,
    trust_packets,
    verification_by_packet_id,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _find_packet_id(evidence_id: str) -> Optional[str]:
    evidence = digital_evidence.get(evidence_id)
    if evidence:
        return evidence.get("packet_id")
    for packet_id, item_id in evidence_by_packet_id.items():
        if item_id == evidence_id:
            return packet_id
    return None


def explain_evidence(evidence_id: str) -> dict[str, Any]:
    packet_id = _find_packet_id(evidence_id)
    if not packet_id:
        return {
            "status": "NOT_FOUND",
            "evidence_id": evidence_id,
            "reason": "EVIDENCE_NOT_FOUND",
        }
    packet = trust_packets.get(packet_id)
    payload = packet.payload if packet else {}
    mrv_id = taxi_mrv_by_packet_id.get(packet_id)
    mrv = taxi_mrv_results.get(mrv_id) if mrv_id else {}
    verification_id = verification_by_packet_id.get(packet_id)
    verification = mrv_verification_records.get(verification_id) if verification_id else {}
    explanation = {
        "explanation_id": _new_id("EEXP"),
        "status": "EXPLAINED",
        "evidence_id": evidence_id,
        "packet_id": packet_id,
        "data_summary": {
            "source_type": payload.get("source_type", "EV_TAXI"),
            "vehicle_id": payload.get("vehicle_id"),
            "operation_date": payload.get("operation_date"),
            "distance_km": payload.get("distance_km"),
            "passenger_count": payload.get("passenger_count"),
            "daily_revenue": payload.get("daily_revenue"),
        },
        "methodology_id": mrv.get("methodology_id"),
        "methodology_version": mrv.get("methodology_version"),
        "verification_process": {
            "verification_id": verification_id,
            "verification_status": verification.get("verification_status"),
            "verification_score": verification.get("verification_score"),
            "completeness_score": verification.get("completeness_score"),
            "integrity_score": verification.get("integrity_score"),
            "source_reliability_score": verification.get("source_reliability_score"),
            "anomaly_flag": verification.get("anomaly_flag"),
        },
        "explanation_text": (
            "이 Evidence는 Trust Packet의 hash, signature, canonical 검증 결과와 "
            "MRV 방법론 버전, Verification Score를 함께 묶은 감사 제출용 근거입니다."
        ),
        "created_at": _now(),
    }
    save_evidence_explanation_memory(explanation)
    return explanation


def explain_packet_evidence(packet_id: str) -> dict[str, Any]:
    trace = get_full_trace_detail(packet_id)
    evidence_id = trace.get("evidence_id")
    if not evidence_id:
        return {"status": "NOT_FOUND", "packet_id": packet_id, "reason": "EVIDENCE_NOT_CREATED"}
    return explain_evidence(evidence_id)
