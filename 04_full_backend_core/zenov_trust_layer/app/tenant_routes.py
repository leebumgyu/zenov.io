from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.billing_service import billing_summary
from .services.subscription_service import get_subscription, list_subscription_plans
from .services.tenant_service import (
    create_tenant,
    resolve_tenant,
    tenant_access_check,
    tenant_dashboard,
    tenant_list_view,
)


router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


class TenantCreateRequest(BaseModel):
    tenant_name: str
    tenant_slug: Optional[str] = None
    tenant_type: str = "TAXI_COMPANY"
    subscription_plan: str = "PILOT"
    admin_email: Optional[str] = None
    status: str = "ACTIVE"


@router.post("")
def create_tenant_view(request: TenantCreateRequest):
    try:
        return create_tenant(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_tenants_view():
    return tenant_list_view()


@router.get("/plans")
def subscription_plans_view():
    return list_subscription_plans()


@router.get("/{tenant_id}/dashboard")
def tenant_dashboard_view(tenant_id: str):
    dashboard = tenant_dashboard(tenant_id)
    if dashboard.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=dashboard)
    return dashboard


@router.get("/{tenant_id}/subscription")
def tenant_subscription_view(tenant_id: str):
    tenant = resolve_tenant(tenant_id)
    resolved_id = tenant["tenant_id"] if tenant else tenant_id
    return get_subscription(resolved_id)


@router.get("/{tenant_id}/billing")
def tenant_billing_view(tenant_id: str):
    tenant = resolve_tenant(tenant_id)
    resolved_id = tenant["tenant_id"] if tenant else tenant_id
    return billing_summary(resolved_id)


@router.get("/{tenant_id}/access-check")
def tenant_access_check_view(tenant_id: str, role: str = "SUPER_ADMIN"):
    tenant = resolve_tenant(tenant_id)
    resolved_id = tenant["tenant_id"] if tenant else tenant_id
    result = tenant_access_check(resolved_id, role)
    if not result.get("allowed"):
        raise HTTPException(status_code=403, detail=result)
    return result
