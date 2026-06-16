from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.commission_engine import default_commission_rule
from .services.merchant_settlement import list_merchant_accounts, simulate_settlement_batch
from .services.settlement_ledger import (
    get_settlement_record,
    list_ledger_entries,
    list_settlement_records,
    update_settlement_status,
)
from .services.settlement_service import simulate_offer_redeem


router = APIRouter(prefix="/api/v1/settlements", tags=["settlements"])


class SettlementSimulationRequest(BaseModel):
    tenant_id: Optional[str] = "ansan-trans"
    driver_id: str = "DRV-001"
    offer_id: str = "OFFER-CHARGE-001"
    merchant_id: str = "ZENOV-CHARGING-PARTNER-001"
    merchant_name: str = "Zenov Charging Partner"
    merchant_type: str = "CHARGING"
    gross_amount_krw: float = 30000
    point_amount: float = 3000
    wallet_transaction_id: Optional[str] = None


class SettlementStatusRequest(BaseModel):
    status: str
    actor: str = "demo-operator"


class SettlementBatchRequest(BaseModel):
    tenant_id: Optional[str] = "ansan-trans"
    batch_period: str = "DAILY"


@router.post("/simulate")
def simulate_settlement_view(request: SettlementSimulationRequest):
    try:
        return simulate_offer_redeem(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_settlements_view(tenant_id: Optional[str] = None, status: Optional[str] = None):
    records = list_settlement_records(tenant_id=tenant_id, status=status)
    return {
        "count": len(records),
        "total_gross_amount_krw": round(sum(float(item.get("gross_amount_krw", 0) or 0) for item in records), 2),
        "total_fee_krw": round(sum(float(item.get("total_fee_krw", 0) or 0) for item in records), 2),
        "total_net_amount_krw": round(sum(float(item.get("net_amount_krw", 0) or 0) for item in records), 2),
        "simulation_only": True,
        "items": records,
    }


@router.get("/commission-rules/default")
def default_commission_rule_view(tenant_id: Optional[str] = "ansan-trans"):
    return default_commission_rule(tenant_id)


@router.get("/merchants")
def list_merchants_view(tenant_id: Optional[str] = None):
    items = list_merchant_accounts(tenant_id)
    return {"count": len(items), "items": items}


@router.post("/batches/simulate")
def simulate_batch_view(request: SettlementBatchRequest):
    return simulate_settlement_batch(tenant_id=request.tenant_id, batch_period=request.batch_period)


@router.get("/{settlement_id}")
def get_settlement_view(settlement_id: str):
    record = get_settlement_record(settlement_id)
    if not record:
        raise HTTPException(status_code=404, detail="SETTLEMENT_NOT_FOUND")
    return {
        "settlement": record,
        "ledger_entries": list_ledger_entries(settlement_id),
        "simulation_only": True,
    }


@router.patch("/{settlement_id}/status")
def update_settlement_status_view(settlement_id: str, request: SettlementStatusRequest):
    try:
        record = update_settlement_status(settlement_id, request.status, actor=request.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": "UPDATED",
        "settlement": record,
        "ledger_entries": list_ledger_entries(settlement_id),
        "simulation_only": True,
    }
