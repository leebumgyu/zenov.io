from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .services.methodology_service import (
    analyze_methodology_change,
    get_methodology_impacts,
    get_registered_methodologies,
    get_registered_methodology,
    register_methodology,
    register_methodology_from_config,
)


router = APIRouter(prefix="/api/v1/methodologies", tags=["methodologies"])


class RegisterMethodologyRequest(BaseModel):
    methodology_id: str = "ZENOV-MOBILITY-MRV-001"
    version: str = "1.0.0"
    effective_date: str = "2026-06-12"
    description: str = "Mobility carbon reduction methodology"
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    status: str = "ACTIVE"
    source_reference: str = "manual"


class ImpactAnalysisRequest(BaseModel):
    methodology_id: str = "ZENOV-MOBILITY-MRV-001"
    from_version: str = "1.0.0"
    to_version: str = "2.0.0"
    baseline_type: str = "lpg_taxi"
    new_baseline_factor: Optional[float] = None
    new_config_snapshot: Optional[dict[str, Any]] = None


@router.post("/bootstrap")
def bootstrap_methodology():
    return register_methodology_from_config()


@router.post("/register")
def register_methodology_view(request: RegisterMethodologyRequest):
    config_snapshot = request.config_snapshot or {
        "methodology": {
            "id": request.methodology_id,
            "version": request.version,
            "effective_date": request.effective_date,
            "description": request.description,
        }
    }
    return register_methodology(
        methodology_id=request.methodology_id,
        version=request.version,
        effective_date=request.effective_date,
        description=request.description,
        config_snapshot=config_snapshot,
        status=request.status,
        source_reference=request.source_reference,
    )


@router.get("")
def list_methodologies_view():
    items = get_registered_methodologies()
    return {"count": len(items), "items": items}


@router.get("/{methodology_id}/{version}")
def get_methodology_view(methodology_id: str, version: str):
    item = get_registered_methodology(methodology_id, version)
    if not item:
        raise HTTPException(status_code=404, detail="Methodology not found")
    return item


@router.post("/impact")
def analyze_methodology_impact_view(request: ImpactAnalysisRequest):
    new_config = request.new_config_snapshot
    if new_config is None:
        source = get_registered_methodology(request.methodology_id, request.from_version)
        if not source:
            raise HTTPException(status_code=404, detail="Source methodology not found")
        new_config = source["config_snapshot"]
        if request.new_baseline_factor is not None:
            new_config = {**new_config}
            emission = {**new_config.get("emission_factors", {})}
            baseline = {**emission.get("baseline", {})}
            factor = {**baseline.get(request.baseline_type, {})}
            factor["value"] = request.new_baseline_factor
            baseline[request.baseline_type] = factor
            emission["baseline"] = baseline
            new_config["emission_factors"] = emission

    try:
        return analyze_methodology_change(
            methodology_id=request.methodology_id,
            from_version=request.from_version,
            to_version=request.to_version,
            baseline_type=request.baseline_type,
            new_config_snapshot=new_config,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/impacts")
def list_methodology_impacts_view():
    items = get_methodology_impacts()
    return {"count": len(items), "items": items}
