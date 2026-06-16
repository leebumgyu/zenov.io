from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..database.crud import get_full_trace_detail
from ..storage import (
    carbon_asset_candidates,
    save_audit_intelligence_explanation_memory,
    taxi_mrv_results,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _find_asset(asset_id: str) -> Optional[dict[str, Any]]:
    if asset_id in carbon_asset_candidates:
        return carbon_asset_candidates[asset_id]
    return next(
        (
            item for item in carbon_asset_candidates.values()
            if item.get("serial_number") == asset_id or item.get("registry_id") == asset_id
        ),
        None,
    )


def explain_packet(packet_id: str, lookup_type: str = "packet", lookup_id: Optional[str] = None) -> dict[str, Any]:
    trace = get_full_trace_detail(packet_id)
    genealogy = {
        "packet_id": trace.get("packet_id"),
        "evidence_id": trace.get("evidence_id"),
        "mrv_id": trace.get("mrv_id"),
        "verification_id": trace.get("verification_id"),
        "asset_id": trace.get("asset_id"),
        "registry_id": trace.get("registry_id"),
        "traceability_status": trace.get("traceability_status"),
    }
    explanation = {
        "explanation_id": _new_id("AIX"),
        "lookup_type": lookup_type,
        "lookup_id": lookup_id or packet_id,
        **genealogy,
        "genealogy": genealogy,
        "explanation_text": (
            f"{genealogy['packet_id']}에서 생성된 데이터는 Evidence {genealogy['evidence_id']}로 봉인되고, "
            f"MRV {genealogy['mrv_id']}와 Verification {genealogy['verification_id']}를 거쳐 "
            f"Asset Candidate {genealogy['asset_id']} 및 Registry 상태로 연결됩니다."
        ),
        "trace": trace,
        "created_at": _now(),
    }
    save_audit_intelligence_explanation_memory(explanation)
    return explanation


def explain_asset(asset_id: str) -> dict[str, Any]:
    asset = _find_asset(asset_id)
    if not asset:
        return {
            "status": "NOT_FOUND",
            "asset_id": asset_id,
            "reason": "ASSET_NOT_FOUND",
            "explanation_text": "요청한 Asset Candidate를 찾을 수 없습니다.",
        }
    mrv = taxi_mrv_results.get(asset.get("mrv_id"))
    packet_id = asset.get("packet_id") or (mrv or {}).get("packet_id")
    if not packet_id:
        return {
            "status": "BROKEN",
            "asset_id": asset_id,
            "reason": "PACKET_LINK_NOT_FOUND",
            "asset": asset,
        }
    explanation = explain_packet(packet_id, lookup_type="asset", lookup_id=asset_id)
    explanation["status"] = "EXPLAINED"
    explanation["asset"] = asset
    return explanation


def explain_latest_asset() -> dict[str, Any]:
    if not carbon_asset_candidates:
        return {
            "status": "NO_ASSET",
            "explanation_text": "아직 설명할 Carbon Asset Candidate가 없습니다. 먼저 143대 CSV Import를 실행하십시오.",
        }
    latest = next(reversed(carbon_asset_candidates.values()))
    return explain_asset(latest["candidate_id"])
