from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import carbon_asset_candidates, copilot_query_logs, save_copilot_query_log_memory
from .audit_intelligence_service import explain_asset, explain_latest_asset
from .billing_service import billing_summary
from .country_service import country_detail
from .kpi_service import portfolio_kpi
from .natural_language_query_engine import classify_question
from .ops_drilldown_service import root_cause_summary


READ_ONLY_ALLOWED_ACTIONS = (
    "Portfolio 설명",
    "Asset 설명",
    "Registry 상태 설명",
    "Compliance 설명",
    "Report 요약",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _log(question: str, actor_role: str, intent: str, response_text: str, source_refs: list[dict[str, Any]], blocked: bool) -> dict[str, Any]:
    log = {
        "query_id": _new_id("AIQ"),
        "actor_role": actor_role,
        "question": question,
        "intent": intent,
        "response_text": response_text,
        "source_refs": source_refs,
        "forbidden_action_blocked": blocked,
        "created_at": _now(),
    }
    save_copilot_query_log_memory(log)
    return log


def _latest_asset_id() -> str | None:
    if not carbon_asset_candidates:
        return None
    return next(reversed(carbon_asset_candidates.values())).get("candidate_id")


def answer_question(question: str, actor_role: str = "EXECUTIVE") -> dict[str, Any]:
    classification = classify_question(question)
    intent = classification["intent"]
    source_refs: list[dict[str, Any]] = []
    data: dict[str, Any] = {}
    blocked = bool(classification.get("forbidden_action_blocked"))

    if blocked:
        response_text = (
            "차단되었습니다. Executive AI Copilot은 읽기 전용입니다. "
            "Asset 생성, Verification 승인, Registry 등록, Methodology 변경은 수행하지 않습니다."
        )
        log = _log(question, actor_role, intent, response_text, [], True)
        return {
            "status": "BLOCKED",
            "intent": intent,
            "answer": response_text,
            "guardrail": "READ_ONLY_COPILOT",
            "allowed_actions": list(READ_ONLY_ALLOWED_ACTIONS),
            "query_log": log,
        }

    if intent in {"PORTFOLIO_REDUCTION", "ASSET_COUNT", "GENERAL_SUMMARY"}:
        portfolio_id = classification.get("entities", {}).get("portfolio_id", "ANSAN_TRANS")
        kpi = portfolio_kpi(portfolio_id)
        current = kpi["current"]
        data = kpi
        source_refs.append({"type": "portfolio_kpi", "portfolio_id": portfolio_id})
        if intent == "ASSET_COUNT":
            response_text = (
                f"{portfolio_id}의 Carbon Asset Candidate는 현재 {current['asset_count']}개입니다. "
                f"연결 차량은 {current['fleet_size']}대이고, 검증 감축량은 "
                f"{current['verified_reduction_tco2e']} tCO2e입니다."
            )
        else:
            response_text = (
                f"이번 포트폴리오 기준 총 검증 감축량은 {current['verified_reduction_tco2e']} tCO2e입니다. "
                f"예상 포트폴리오 가치는 {current['portfolio_value_krw']} KRW입니다."
            )
    elif intent == "COUNTRY_STATUS":
        country_code = classification.get("entities", {}).get("country_code", "TH")
        detail = country_detail(country_code)
        profile = detail.get("country", detail)
        data = detail
        source_refs.append({"type": "country_profile", "country_code": country_code})
        response_text = (
            f"{country_code} 프로젝트는 설정 기반 국가 프로필이 준비되어 있습니다. "
            f"통화는 {profile.get('currency_code')}, 언어는 {profile.get('language_code')}, "
            f"Registry는 {detail.get('registry_profile', {}).get('local_registry', 'configured')}입니다."
        )
    elif intent == "VERIFICATION_REJECT_REASON":
        summary = root_cause_summary()
        top = (summary.get("top_10_reason_codes") or [{}])[0]
        data = summary
        source_refs.append({"type": "root_cause_summary"})
        if top.get("reason_code"):
            response_text = f"가장 많은 Verification/Import 실패 원인은 {top['reason_code']}이며 {top['count']}건입니다."
        else:
            response_text = "현재 기록된 Verification Reject 또는 Import 실패 원인은 없습니다."
    elif intent == "MRR":
        tenant_id = classification.get("entities", {}).get("tenant_id", "ansan-trans")
        billing = billing_summary(tenant_id)
        data = billing
        source_refs.append({"type": "billing_summary", "tenant_id": tenant_id})
        response_text = (
            f"{tenant_id}의 현재 월 반복 매출 추정치는 "
            f"{billing['next_invoice_estimate_krw']} {billing['currency']}입니다. "
            f"플랜은 {billing['subscription']['plan']}입니다."
        )
    elif intent == "AUDIT_ASSET_GENEALOGY":
        asset_id = _latest_asset_id()
        data = explain_asset(asset_id) if asset_id else explain_latest_asset()
        source_refs.append({"type": "audit_intelligence", "asset_id": asset_id})
        response_text = data.get("explanation_text", "설명 가능한 Asset 계보가 아직 없습니다.")
    else:
        data = portfolio_kpi("ANSAN_TRANS")
        source_refs.append({"type": "portfolio_kpi", "portfolio_id": "ANSAN_TRANS"})
        response_text = (
            "Zenov Copilot은 현재 Portfolio, Asset, Registry, Compliance, Report 요약을 읽기 전용으로 설명합니다. "
            "자산 생성이나 검증 승인은 수행하지 않습니다."
        )

    log = _log(question, actor_role, intent, response_text, source_refs, False)
    return {
        "status": "ANSWERED",
        "intent": intent,
        "confidence": classification.get("confidence"),
        "answer": response_text,
        "guardrail": "READ_ONLY_COPILOT",
        "allowed_actions": list(READ_ONLY_ALLOWED_ACTIONS),
        "source_refs": source_refs,
        "data": data,
        "query_log": log,
    }


def list_query_logs(limit: int = 50) -> dict[str, Any]:
    items = list(reversed(copilot_query_logs))[:limit]
    return {"count": len(items), "items": items}
