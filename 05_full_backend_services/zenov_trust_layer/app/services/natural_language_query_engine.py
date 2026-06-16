from __future__ import annotations

from typing import Any


FORBIDDEN_PATTERNS = (
    "생성해",
    "만들어줘",
    "승인해",
    "등록해",
    "변경해",
    "삭제해",
    "발행해",
    "asset 생성",
    "verification 승인",
    "registry 등록",
    "methodology 변경",
    "방법론 변경",
    "자산 생성",
    "검증 승인",
    "레지스트리 등록",
    "탄소배출권 발행",
)


def classify_question(question: str) -> dict[str, Any]:
    normalized = question.strip().lower()
    blocked = any(pattern in normalized for pattern in FORBIDDEN_PATTERNS)
    if blocked:
        return {
            "intent": "FORBIDDEN_ACTION",
            "confidence": 0.99,
            "forbidden_action_blocked": True,
            "entities": {},
        }
    if "reject" in normalized or "거절" in normalized or "원인" in normalized or "verification" in normalized:
        return {"intent": "VERIFICATION_REJECT_REASON", "confidence": 0.86, "entities": {}}
    if "태국" in normalized or "thailand" in normalized or "thai" in normalized:
        return {"intent": "COUNTRY_STATUS", "confidence": 0.9, "entities": {"country_code": "TH"}}
    if "말레이" in normalized or "malaysia" in normalized:
        return {"intent": "COUNTRY_STATUS", "confidence": 0.9, "entities": {"country_code": "MY"}}
    if "mrr" in normalized or "매출" in normalized or "구독료" in normalized:
        return {"intent": "MRR", "confidence": 0.84, "entities": {"tenant_id": "ansan-trans"}}
    if "asset" in normalized or "자산" in normalized or "몇 개" in normalized or "안산교통" in normalized:
        return {"intent": "ASSET_COUNT", "confidence": 0.88, "entities": {"portfolio_id": "ANSAN_TRANS"}}
    if "ast-" in normalized or "근거" in normalized or "어떤 근거" in normalized:
        return {"intent": "AUDIT_ASSET_GENEALOGY", "confidence": 0.82, "entities": {}}
    if "감축량" in normalized or "총 감축" in normalized or "co2" in normalized or "co₂" in normalized:
        return {"intent": "PORTFOLIO_REDUCTION", "confidence": 0.86, "entities": {"portfolio_id": "ANSAN_TRANS"}}
    return {"intent": "GENERAL_SUMMARY", "confidence": 0.62, "entities": {"portfolio_id": "ANSAN_TRANS"}}
