from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .services.auth_service import (
    auth_admin_summary,
    auth_audit,
    confirm_password_reset,
    get_current_auth,
    partner_login,
    referral_login,
    request_password_reset,
)


router = APIRouter(prefix="/api/v1/auth", tags=["partner-referral-auth"])


class PartnerLoginRequest(BaseModel):
    partner_code: str
    password: str


class ReferralLoginRequest(BaseModel):
    referral_code: str
    password: str


class PasswordResetRequest(BaseModel):
    account_type: str = Field(pattern="^(PARTNER|REFERRAL|partner|referral)$")
    code: str


class PasswordResetConfirmRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)


@router.post("/partner/login")
def partner_login_view(request: PartnerLoginRequest):
    try:
        return partner_login(request.partner_code, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        status_code = 423 if str(exc) == "ACCOUNT_LOCKED" else 401 if str(exc) == "INVALID_CREDENTIALS" else 403
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.post("/referral/login")
def referral_login_view(request: ReferralLoginRequest):
    try:
        return referral_login(request.referral_code, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except PermissionError as exc:
        status_code = 423 if str(exc) == "ACCOUNT_LOCKED" else 401 if str(exc) == "INVALID_CREDENTIALS" else 403
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.post("/password-reset/request")
def password_reset_request_view(request: PasswordResetRequest):
    return request_password_reset(request.account_type, request.code)


@router.post("/password-reset/confirm")
def password_reset_confirm_view(request: PasswordResetConfirmRequest):
    try:
        return confirm_password_reset(request.reset_token, request.new_password)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/me")
def auth_me_view(authorization: Optional[str] = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="AUTHORIZATION_REQUIRED")
    try:
        return get_current_auth(authorization)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/summary")
def auth_summary_view():
    return auth_admin_summary()


@router.get("/audit")
def auth_audit_view(subject_code: Optional[str] = None):
    return auth_audit(subject_code)
