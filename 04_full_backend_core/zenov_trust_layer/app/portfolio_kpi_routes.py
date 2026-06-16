from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .services.kpi_service import DEFAULT_PORTFOLIO_ID, list_kpi_snapshots, portfolio_kpi, save_kpi_snapshot
from .services.target_management_service import get_portfolio_target, upsert_portfolio_target


router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio-kpi"])


class PortfolioTargetRequest(BaseModel):
    portfolio_id: str = DEFAULT_PORTFOLIO_ID
    target_vehicle_count: int = Field(default=500, ge=0)
    target_reduction_tco2e: float = Field(default=1000.0, ge=0)
    target_asset_count: int = Field(default=300, ge=0)
    target_registry_count: int = Field(default=120, ge=0)
    target_portfolio_value: float = Field(default=1_000_000_000.0, ge=0)
    currency: str = "KRW"


@router.get("/kpi")
def get_portfolio_kpi(portfolio_id: str = DEFAULT_PORTFOLIO_ID):
    return portfolio_kpi(portfolio_id)


@router.post("/targets")
def save_portfolio_target(request: PortfolioTargetRequest):
    target = upsert_portfolio_target(**request.model_dump())
    return {
        "status": "SAVED",
        "target": target,
        "kpi": portfolio_kpi(request.portfolio_id),
    }


@router.get("/targets/{portfolio_id}")
def get_target(portfolio_id: str):
    return get_portfolio_target(portfolio_id)


@router.post("/kpi/snapshot")
def create_kpi_snapshot(period: str = "DAILY", portfolio_id: str = DEFAULT_PORTFOLIO_ID):
    return save_kpi_snapshot(period=period.upper(), portfolio_id=portfolio_id)


@router.get("/kpi/snapshots")
def get_kpi_snapshots(portfolio_id: str = DEFAULT_PORTFOLIO_ID, period: Optional[str] = None):
    items = list_kpi_snapshots(portfolio_id)
    if period:
        items = [item for item in items if item.get("period") == period.upper()]
    return {"portfolio_id": portfolio_id, "count": len(items), "items": items}
