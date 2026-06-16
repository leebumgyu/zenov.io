from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.customer_success_service import (
    complete_milestone,
    create_health_snapshot,
    customer_success_dashboard,
    list_customer_success_projects,
    start_onboarding,
)
from .services.deployment_template_engine import (
    bootstrap_deployment_templates,
    create_deployment_template,
    list_deployment_templates,
)


router = APIRouter(prefix="/api/v1/customer-success", tags=["customer-success"])


class OnboardingStartRequest(BaseModel):
    customer_name: str = "Ansan Transport"
    industry_type: str = "TAXI"
    tenant_id: Optional[str] = "ansan-trans"
    partner_id: Optional[str] = "ANSAN_TRANS"
    template_id: Optional[str] = None


class MilestoneCompleteRequest(BaseModel):
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None


class TemplateCreateRequest(BaseModel):
    industry_type: str
    template_name: str
    connector_type: str
    supported_sources: Optional[list[str]] = None
    required_fields: Optional[list[str]] = None
    validation_rules: Optional[list[str]] = None
    default_mapping: Optional[dict[str, str]] = None


@router.post("/onboarding/start")
def start_onboarding_view(request: OnboardingStartRequest):
    try:
        return start_onboarding(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/onboarding")
def list_onboarding_view():
    return list_customer_success_projects()


@router.get("/onboarding/{onboarding_id}/dashboard")
def onboarding_dashboard_view(onboarding_id: str):
    dashboard = customer_success_dashboard(onboarding_id)
    if dashboard.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=dashboard)
    return dashboard


@router.post("/onboarding/{onboarding_id}/milestones/{milestone_key}/complete")
def complete_milestone_view(onboarding_id: str, milestone_key: str, request: MilestoneCompleteRequest):
    try:
        return complete_milestone(
            onboarding_id=onboarding_id,
            milestone_key=milestone_key,
            evidence_ref=request.evidence_ref,
            notes=request.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/onboarding/{onboarding_id}/health-snapshot")
def health_snapshot_view(onboarding_id: str):
    try:
        return create_health_snapshot(onboarding_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/templates/bootstrap")
def bootstrap_templates_view():
    return {"status": "BOOTSTRAPPED", "items": bootstrap_deployment_templates()}


@router.get("/templates")
def templates_view(industry_type: Optional[str] = None):
    items = list_deployment_templates(industry_type)
    return {"count": len(items), "items": items}


@router.post("/templates")
def create_template_view(request: TemplateCreateRequest):
    return create_deployment_template(**request.model_dump())
