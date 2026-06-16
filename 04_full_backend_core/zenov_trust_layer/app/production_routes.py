from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.production_dashboard_service import production_dashboard
from .services.production_readiness_service import (
    bootstrap_readiness_checks,
    list_runbooks,
    readiness_summary,
    update_readiness_check,
)
from .services.sla_monitoring_service import calculate_sla_snapshot, latest_sla_snapshot


router = APIRouter(prefix="/api/v1/production", tags=["production"])


class ReadinessUpdateRequest(BaseModel):
    status: str = "PASS"
    evidence_ref: Optional[str] = None


@router.get("/dashboard")
def production_dashboard_view(tenant_id: Optional[str] = "ansan-trans", onboarding_id: Optional[str] = None):
    return production_dashboard(tenant_id=tenant_id, onboarding_id=onboarding_id)


@router.post("/readiness/bootstrap")
def bootstrap_readiness_view(tenant_id: Optional[str] = "ansan-trans"):
    return {"status": "BOOTSTRAPPED", "items": bootstrap_readiness_checks(tenant_id)}


@router.get("/readiness")
def readiness_view(tenant_id: Optional[str] = "ansan-trans"):
    return readiness_summary(tenant_id)


@router.patch("/readiness/{check_id}")
def update_readiness_view(check_id: str, request: ReadinessUpdateRequest):
    try:
        return update_readiness_check(check_id, request.status, evidence_ref=request.evidence_ref)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sla/snapshot")
def sla_snapshot_view(tenant_id: Optional[str] = "ansan-trans"):
    return calculate_sla_snapshot(tenant_id)


@router.get("/sla/latest")
def latest_sla_view(tenant_id: Optional[str] = "ansan-trans"):
    return latest_sla_snapshot(tenant_id)


@router.get("/runbooks")
def runbooks_view(tenant_id: Optional[str] = "ansan-trans"):
    return list_runbooks(tenant_id)
