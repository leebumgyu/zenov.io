from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.language_reviewer import reviewer_summary
from .services.localization_review_service import (
    approve_translation,
    create_or_update_translation_key,
    language_status,
    reject_translation,
    resolve_translation,
    review_history,
    submit_translation_review,
    translation_keys_view,
)


router = APIRouter(prefix="/api/v1/localization", tags=["localization-review"])


class TranslationKeyRequest(BaseModel):
    key_name: str
    language_code: str
    target_area: str
    source_text: str
    translated_text: str
    status: str = "DRAFT"
    requires_legal_review: bool = False
    fallback_text: Optional[str] = None


class TranslationReviewRequest(BaseModel):
    translation_key_id: str
    reviewer_id: str
    review_action: str = "IN_REVIEW"
    comment: str = ""


class TranslationApproveRequest(BaseModel):
    translation_key_id: str
    reviewer_id: str
    publish: bool = False


class TranslationRejectRequest(BaseModel):
    translation_key_id: str
    reviewer_id: str
    reason: str = ""


@router.get("/keys")
def localization_keys_view(language_code: Optional[str] = None, status: Optional[str] = None):
    return translation_keys_view(language_code, status)


@router.post("/keys")
def create_translation_key_view(request: TranslationKeyRequest):
    try:
        return create_or_update_translation_key(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/review")
def review_translation_view(request: TranslationReviewRequest):
    try:
        return submit_translation_review(**request.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/approve")
def approve_translation_view(request: TranslationApproveRequest):
    try:
        return approve_translation(**request.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reject")
def reject_translation_view(request: TranslationRejectRequest):
    try:
        return reject_translation(**request.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status/{language_code}")
def localization_status_view(language_code: str):
    return language_status(language_code)


@router.get("/resolve/{language_code}/{key_name}")
def resolve_translation_view(language_code: str, key_name: str):
    return resolve_translation(key_name, language_code)


@router.get("/reviewers")
def language_reviewers_view(language_code: Optional[str] = None):
    return reviewer_summary(language_code)


@router.get("/reviews/{translation_key_id}")
def translation_review_history_view(translation_key_id: str):
    return review_history(translation_key_id)
