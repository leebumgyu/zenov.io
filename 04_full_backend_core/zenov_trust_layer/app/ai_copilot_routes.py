from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .services.audit_intelligence_service import explain_asset, explain_latest_asset
from .services.evidence_explainer import explain_evidence
from .services.executive_copilot_service import answer_question, list_query_logs


router = APIRouter(prefix="/api/v1/copilot", tags=["executive-ai-copilot"])


class CopilotQueryRequest(BaseModel):
    question: str
    actor_role: str = "EXECUTIVE"


@router.post("/query")
def copilot_query_view(request: CopilotQueryRequest):
    return answer_question(request.question, actor_role=request.actor_role)


@router.get("/query-logs")
def copilot_query_logs_view(limit: Optional[int] = 50):
    return list_query_logs(limit or 50)


@router.get("/audit/asset/latest")
def explain_latest_asset_view():
    return explain_latest_asset()


@router.get("/audit/asset/{asset_id}")
def explain_asset_view(asset_id: str):
    return explain_asset(asset_id)


@router.get("/evidence/{evidence_id}")
def explain_evidence_view(evidence_id: str):
    return explain_evidence(evidence_id)


@router.get("/examples")
def copilot_examples_view():
    return {
        "examples": [
            "이번 달 총 감축량은?",
            "안산교통 Asset은 몇 개인가?",
            "태국 프로젝트 상태는?",
            "Verification Reject 원인은?",
            "MRR은 얼마인가?",
            "AST-2026-0001은 어떤 근거로 생성되었는가?",
            "Registry 등록해줘",
        ],
        "rule": "AI is read-only. It explains verified Trust Chain data and cannot create, approve, register, or change methodology.",
    }
