from __future__ import annotations

from typing import Any

from ..database.translation_review_crud import get_language_reviewer, list_language_reviewers, save_language_reviewer


REVIEWER_ROLES = {"LANGUAGE_ADMIN", "COUNTRY_REVIEWER", "LEGAL_REVIEWER"}


def seed_default_reviewers() -> None:
    defaults = [
        {
            "reviewer_id": "LRV-LANGUAGE-ADMIN",
            "reviewer_name": "Zenov Language Admin",
            "reviewer_role": "LANGUAGE_ADMIN",
            "language_code": "*",
            "assigned_languages": ["ko-KR", "en-US", "th-TH", "vi-VN", "zh-CN"],
            "status": "ACTIVE",
        },
        {
            "reviewer_id": "LRV-LEGAL-001",
            "reviewer_name": "Zenov Legal Reviewer",
            "reviewer_role": "LEGAL_REVIEWER",
            "language_code": "*",
            "assigned_languages": ["ko-KR", "en-US", "th-TH", "vi-VN", "zh-CN"],
            "status": "ACTIVE",
        },
        {
            "reviewer_id": "LRV-TH-001",
            "reviewer_name": "Thailand Country Reviewer",
            "reviewer_role": "COUNTRY_REVIEWER",
            "language_code": "th-TH",
            "assigned_languages": ["th-TH"],
            "status": "ACTIVE",
        },
        {
            "reviewer_id": "LRV-VN-001",
            "reviewer_name": "Vietnam Country Reviewer",
            "reviewer_role": "COUNTRY_REVIEWER",
            "language_code": "vi-VN",
            "assigned_languages": ["vi-VN"],
            "status": "ACTIVE",
        },
    ]
    for reviewer in defaults:
        if not get_language_reviewer(reviewer["reviewer_id"]):
            save_language_reviewer(reviewer)


def reviewer_can_review(reviewer: dict[str, Any], translation: dict[str, Any]) -> bool:
    if reviewer.get("status") != "ACTIVE":
        return False
    role = reviewer.get("reviewer_role")
    if role == "LANGUAGE_ADMIN":
        return True
    if role == "LEGAL_REVIEWER":
        return bool(translation.get("requires_legal_review"))
    if role == "COUNTRY_REVIEWER":
        return translation.get("language_code") in set(reviewer.get("assigned_languages", []))
    return False


def reviewer_can_publish(reviewer: dict[str, Any], translation: dict[str, Any]) -> bool:
    if reviewer.get("status") != "ACTIVE":
        return False
    if translation.get("requires_legal_review"):
        return reviewer.get("reviewer_role") == "LEGAL_REVIEWER"
    return reviewer.get("reviewer_role") in {"LANGUAGE_ADMIN", "COUNTRY_REVIEWER"}


def reviewer_summary(language_code: str | None = None) -> dict[str, Any]:
    seed_default_reviewers()
    reviewers = list_language_reviewers(language_code)
    return {"count": len(reviewers), "items": reviewers}
