from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.asset_transfer_service import transfer_asset
from .services.ownership_service import get_asset_ownership, list_asset_history, ownership_summary


router = APIRouter(prefix="/api/v1/assets", tags=["asset-ownership"])


class AssetTransferRequest(BaseModel):
    asset_id: str
    to_owner_entity: str
    to_owner_type: str
    transfer_reason: str = "COMMERCIAL_TRANSFER_SIMULATION"
    actor: str = "demo-operator"
    transfer_reference: Optional[str] = None


@router.get("/ownership/summary")
def ownership_summary_view():
    return ownership_summary()


@router.get("/{asset_id}/ownership")
def asset_ownership_view(asset_id: str):
    try:
        return get_asset_ownership(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/transfer")
def asset_transfer_view(request: AssetTransferRequest):
    try:
        return transfer_asset(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{asset_id}/history")
def asset_history_view(asset_id: str):
    try:
        return list_asset_history(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
