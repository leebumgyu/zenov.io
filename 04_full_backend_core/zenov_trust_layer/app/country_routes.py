from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.country_config_registry import bootstrap_country_profiles
from .services.country_service import add_country_from_config, country_dashboard, country_detail
from .services.localization_engine import localize_report_snapshot
from .services.methodology_adapter import create_methodology_adapter, list_methodology_adapters


router = APIRouter(prefix="/api/v1/countries", tags=["countries"])


class CountryAddRequest(BaseModel):
    country_code: str


class MethodologyAdapterRequest(BaseModel):
    country_code: str
    industry_type: str = "TAXI"
    base_methodology_id: str = "ZENOV-MOBILITY-MRV-001"
    local_methodology_id: Optional[str] = None
    local_methodology_version: str = "draft"
    adapter_status: str = "DRAFT"


class ReportLocalizationRequest(BaseModel):
    country_code: str
    report_snapshot: dict = {}


@router.post("/bootstrap")
def bootstrap_countries_view():
    return {"status": "BOOTSTRAPPED", "items": bootstrap_country_profiles()}


@router.get("")
def country_dashboard_view():
    return country_dashboard()


@router.post("")
def add_country_view(request: CountryAddRequest):
    try:
        return add_country_from_config(request.country_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{country_code}")
def country_detail_view(country_code: str):
    try:
        return country_detail(country_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/methodology-adapters")
def create_adapter_view(request: MethodologyAdapterRequest):
    try:
        return create_methodology_adapter(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/methodology-adapters/list")
def list_adapters_view(country_code: Optional[str] = None):
    items = list_methodology_adapters(country_code)
    return {"count": len(items), "items": items}


@router.post("/reports/localize")
def localize_report_view(request: ReportLocalizationRequest):
    try:
        return localize_report_snapshot(request.country_code, request.report_snapshot)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
