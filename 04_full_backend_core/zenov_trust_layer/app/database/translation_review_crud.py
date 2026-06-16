from __future__ import annotations

from typing import Any, Optional

from ..storage import (
    language_reviewers,
    save_language_reviewer_memory,
    save_translation_key_memory,
    save_translation_review_memory,
    translation_keys,
    translation_reviews,
)


def save_translation_key(key: dict[str, Any]) -> dict[str, Any]:
    save_translation_key_memory(key)
    return key


def get_translation_key(translation_key_id: str) -> Optional[dict[str, Any]]:
    return translation_keys.get(translation_key_id)


def find_translation_key(key_name: str, language_code: str) -> Optional[dict[str, Any]]:
    return next(
        (
            item
            for item in translation_keys.values()
            if item.get("key_name") == key_name and item.get("language_code") == language_code
        ),
        None,
    )


def list_translation_keys(language_code: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    items = list(translation_keys.values())
    if language_code:
        items = [item for item in items if item.get("language_code") == language_code]
    if status:
        items = [item for item in items if item.get("status") == status]
    return sorted(items, key=lambda item: (item.get("language_code", ""), item.get("key_name", "")))


def save_translation_review(review: dict[str, Any]) -> dict[str, Any]:
    save_translation_review_memory(review)
    return review


def list_translation_reviews(translation_key_id: str | None = None) -> list[dict[str, Any]]:
    items = list(translation_reviews.values())
    if translation_key_id:
        items = [item for item in items if item.get("translation_key_id") == translation_key_id]
    return sorted(items, key=lambda item: item.get("created_at", ""))


def save_language_reviewer(reviewer: dict[str, Any]) -> dict[str, Any]:
    save_language_reviewer_memory(reviewer)
    return reviewer


def get_language_reviewer(reviewer_id: str) -> Optional[dict[str, Any]]:
    return language_reviewers.get(reviewer_id)


def list_language_reviewers(language_code: str | None = None, role: str | None = None) -> list[dict[str, Any]]:
    items = list(language_reviewers.values())
    if language_code:
        items = [
            item
            for item in items
            if item.get("language_code") in {language_code, "*"} or language_code in item.get("assigned_languages", [])
        ]
    if role:
        items = [item for item in items if item.get("reviewer_role") == role]
    return sorted(items, key=lambda item: item.get("reviewer_name", ""))
