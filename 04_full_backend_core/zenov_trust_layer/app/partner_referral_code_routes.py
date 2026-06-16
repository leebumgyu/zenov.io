from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.auth_service import (
    create_partner_code,
    create_referral_code,
    disable_partner_code,
    disable_referral_code,
    list_partner_codes,
    list_referral_codes,
    update_partner_code,
    update_referral_code,
    verify_partner_code,
    verify_referral_code,
)


partner_router = APIRouter(prefix="/api/v1/partner-codes", tags=["partner-codes"])
referral_router = APIRouter(prefix="/api/v1/referral-codes", tags=["referral-codes"])


class PartnerCodeCreateRequest(BaseModel):
    partner_code: str
    partner_name: str
    password: str
    tenant_id: str
    sub_unit_code: str = ""
    contract_status: str = "ACTIVE"
    role: str = "PARTNER_ADMIN"
    status: str = "ACTIVE"


class PartnerCodeVerifyRequest(BaseModel):
    partner_code: str
    password: str


class PartnerCodeUpdateRequest(BaseModel):
    partner_code: str
    partner_name: Optional[str] = None
    tenant_id: Optional[str] = None
    sub_unit_code: Optional[str] = None
    contract_status: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None


class PartnerCodeDisableRequest(BaseModel):
    partner_code: str


class ReferralCodeCreateRequest(BaseModel):
    referral_code: str
    owner_type: str = "INDIVIDUAL"
    owner_name: str
    password: str
    linked_partner_code: str
    linked_sub_unit_code: str = ""
    reward_policy_id: str
    role: str = "REFERRAL_OWNER"
    status: str = "ACTIVE"


class ReferralCodeVerifyRequest(BaseModel):
    referral_code: str
    password: str


class ReferralCodeUpdateRequest(BaseModel):
    referral_code: str
    owner_type: Optional[str] = None
    owner_name: Optional[str] = None
    linked_partner_code: Optional[str] = None
    linked_sub_unit_code: Optional[str] = None
    reward_policy_id: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None


class ReferralCodeDisableRequest(BaseModel):
    referral_code: str


@partner_router.post("/create")
def create_partner_code_view(request: PartnerCodeCreateRequest):
    try:
        return create_partner_code(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@partner_router.post("/verify")
def verify_partner_code_view(request: PartnerCodeVerifyRequest):
    try:
        return verify_partner_code(request.partner_code, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@partner_router.get("/list")
def list_partner_codes_view():
    return list_partner_codes()


@partner_router.post("/update")
def update_partner_code_view(request: PartnerCodeUpdateRequest):
    try:
        return update_partner_code(request.partner_code, request.model_dump(exclude={"partner_code"}))
    except ValueError as exc:
        raise HTTPException(status_code=404 if str(exc) == "PARTNER_CODE_NOT_FOUND" else 400, detail=str(exc)) from exc


@partner_router.post("/disable")
def disable_partner_code_view(request: PartnerCodeDisableRequest):
    try:
        return disable_partner_code(request.partner_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@referral_router.post("/create")
def create_referral_code_view(request: ReferralCodeCreateRequest):
    try:
        return create_referral_code(**request.model_dump())
    except ValueError as exc:
        status_code = 400
        if str(exc) == "LINKED_PARTNER_CODE_NOT_FOUND":
            status_code = 404
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@referral_router.post("/verify")
def verify_referral_code_view(request: ReferralCodeVerifyRequest):
    try:
        return verify_referral_code(request.referral_code, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@referral_router.get("/list")
def list_referral_codes_view():
    return list_referral_codes()


@referral_router.post("/update")
def update_referral_code_view(request: ReferralCodeUpdateRequest):
    try:
        return update_referral_code(request.referral_code, request.model_dump(exclude={"referral_code"}))
    except ValueError as exc:
        status_code = 400
        if str(exc) in {"REFERRAL_CODE_NOT_FOUND", "LINKED_PARTNER_CODE_NOT_FOUND"}:
            status_code = 404
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@referral_router.post("/disable")
def disable_referral_code_view(request: ReferralCodeDisableRequest):
    try:
        return disable_referral_code(request.referral_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
