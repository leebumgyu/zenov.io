from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..database.translation_review_crud import (
    find_translation_key,
    get_translation_key,
    list_translation_keys,
    list_translation_reviews,
    save_translation_key,
    save_translation_review,
)
from .language_reviewer import get_language_reviewer, reviewer_can_publish, reviewer_can_review, seed_default_reviewers


STATUSES = {"DRAFT", "MACHINE_TRANSLATED", "IN_REVIEW", "APPROVED", "REJECTED", "PUBLISHED"}
LANGUAGES = ("ko-KR", "en-US", "th-TH", "vi-VN", "zh-CN")
REVIEW_TARGETS = (
    "UI_MENU",
    "ERROR_MESSAGE",
    "MRV_REPORT",
    "CARBON_TRUST_CERTIFICATE",
    "PARTNER_DASHBOARD",
    "REFERRAL_DASHBOARD",
    "WALLET_POINT",
    "LEGAL_CERTIFICATION_SETTLEMENT",
)


CORE_TRANSLATIONS = {
    "menu.customer_zero": {
        "target_area": "UI_MENU",
        "requires_legal_review": False,
        "values": {
            "ko-KR": "Customer Zero",
            "en-US": "Customer Zero",
            "th-TH": "ลูกค้าเริ่มต้น",
            "vi-VN": "Khach hang dau tien",
            "zh-CN": "首个客户",
        },
    },
    "menu.partner_codes": {
        "target_area": "PARTNER_DASHBOARD",
        "requires_legal_review": False,
        "values": {
            "ko-KR": "Partner Codes",
            "en-US": "Partner Codes",
            "th-TH": "รหัสพันธมิตร",
            "vi-VN": "Ma doi tac",
            "zh-CN": "合作伙伴代码",
        },
    },
    "menu.referral_codes": {
        "target_area": "REFERRAL_DASHBOARD",
        "requires_legal_review": False,
        "values": {
            "ko-KR": "Referral Codes",
            "en-US": "Referral Codes",
            "th-TH": "รหัสแนะนำ",
            "vi-VN": "Ma gioi thieu",
            "zh-CN": "推荐代码",
        },
    },
    "certificate.carbon_asset_candidate": {
        "target_area": "CARBON_TRUST_CERTIFICATE",
        "requires_legal_review": True,
        "values": {
            "ko-KR": "Carbon Asset Candidate",
            "en-US": "Carbon Asset Candidate",
            "th-TH": "ข้อมูลผู้สมัครสินทรัพย์คาร์บอน",
            "vi-VN": "Ung vien tai san carbon",
            "zh-CN": "碳资产候选数据",
        },
    },
    "legal.no_credit_before_certification": {
        "target_area": "LEGAL_CERTIFICATION_SETTLEMENT",
        "requires_legal_review": True,
        "values": {
            "ko-KR": "실제 인증 전에는 Carbon Asset Candidate 또는 Verified Carbon Data로 표현합니다.",
            "en-US": "Before external certification, use Carbon Asset Candidate or Verified Carbon Data.",
            "th-TH": "ก่อนการรับรองภายนอก ให้ใช้ Carbon Asset Candidate หรือ Verified Carbon Data",
            "vi-VN": "Truoc chung nhan ben ngoai, su dung Carbon Asset Candidate hoac Verified Carbon Data.",
            "zh-CN": "外部认证前，使用碳资产候选数据或已验证碳数据表述。",
        },
    },
    "report.verified_carbon_data": {
        "target_area": "MRV_REPORT",
        "requires_legal_review": True,
        "values": {
            "ko-KR": "Verified Carbon Data",
            "en-US": "Verified Carbon Data",
            "th-TH": "ข้อมูลคาร์บอนที่ตรวจสอบแล้ว",
            "vi-VN": "Du lieu carbon da xac minh",
            "zh-CN": "已验证碳数据",
        },
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def seed_core_translation_keys() -> None:
    seed_default_reviewers()
    for key_name, definition in CORE_TRANSLATIONS.items():
        for language_code in LANGUAGES:
            if find_translation_key(key_name, language_code):
                continue
            status = "APPROVED"
            translation = {
                "translation_key_id": _new_id("TRK"),
                "key_name": key_name,
                "language_code": language_code,
                "target_area": definition["target_area"],
                "source_text": definition["values"]["en-US"],
                "translated_text": definition["values"][language_code],
                "fallback_text": definition["values"]["en-US"],
                "status": status,
                "requires_legal_review": bool(definition["requires_legal_review"]),
                "legal_review_status": "APPROVED" if definition["requires_legal_review"] else "NOT_REQUIRED",
                "created_at": _now(),
                "updated_at": _now(),
                "published_at": None,
            }
            save_translation_key(translation)
            save_translation_review(
                {
                    "review_id": _new_id("TRV"),
                    "translation_key_id": translation["translation_key_id"],
                    "reviewer_id": "LRV-LEGAL-001" if translation["requires_legal_review"] else "LRV-LANGUAGE-ADMIN",
                    "reviewer_role": "LEGAL_REVIEWER" if translation["requires_legal_review"] else "LANGUAGE_ADMIN",
                    "review_action": "APPROVED",
                    "from_status": "IN_REVIEW",
                    "to_status": "APPROVED",
                    "comment": "Seeded core phrase approved for demo review workflow.",
                    "created_at": _now(),
                }
            )


def create_or_update_translation_key(
    *,
    key_name: str,
    language_code: str,
    target_area: str,
    source_text: str,
    translated_text: str,
    status: str = "DRAFT",
    requires_legal_review: bool = False,
    fallback_text: str | None = None,
) -> dict[str, Any]:
    seed_core_translation_keys()
    if language_code not in LANGUAGES:
        raise ValueError("UNSUPPORTED_LANGUAGE")
    if target_area not in REVIEW_TARGETS:
        raise ValueError("UNSUPPORTED_REVIEW_TARGET")
    if status not in STATUSES:
        raise ValueError("UNSUPPORTED_TRANSLATION_STATUS")
    if "Carbon Credit" in translated_text and requires_legal_review is False:
        requires_legal_review = True
    existing = find_translation_key(key_name, language_code)
    record = existing or {
        "translation_key_id": _new_id("TRK"),
        "key_name": key_name,
        "language_code": language_code,
        "created_at": _now(),
    }
    record.update(
        {
            "target_area": target_area,
            "source_text": source_text,
            "translated_text": translated_text.replace("Carbon Credit", "Carbon Asset Candidate"),
            "fallback_text": fallback_text or source_text,
            "status": status,
            "requires_legal_review": requires_legal_review,
            "legal_review_status": "PENDING" if requires_legal_review else "NOT_REQUIRED",
            "updated_at": _now(),
            "published_at": record.get("published_at"),
        }
    )
    save_translation_key(record)
    return record


def translation_keys_view(language_code: str | None = None, status: str | None = None) -> dict[str, Any]:
    seed_core_translation_keys()
    items = list_translation_keys(language_code, status)
    return {
        "count": len(items),
        "items": items,
        "rule": "Only APPROVED or PUBLISHED translations can be exposed to production UI. Missing translations fallback to en-US.",
    }


def submit_translation_review(
    *,
    translation_key_id: str,
    reviewer_id: str,
    review_action: str = "IN_REVIEW",
    comment: str = "",
) -> dict[str, Any]:
    seed_core_translation_keys()
    translation = get_translation_key(translation_key_id)
    if not translation:
        raise ValueError("TRANSLATION_KEY_NOT_FOUND")
    reviewer = get_language_reviewer(reviewer_id)
    if not reviewer:
        raise ValueError("REVIEWER_NOT_FOUND")
    if not reviewer_can_review(reviewer, translation):
        raise PermissionError("REVIEWER_NOT_ALLOWED")
    previous = translation["status"]
    if review_action == "IN_REVIEW":
        next_status = "IN_REVIEW"
    elif review_action == "APPROVED":
        next_status = "APPROVED"
    elif review_action == "REJECTED":
        next_status = "REJECTED"
    else:
        raise ValueError("UNSUPPORTED_REVIEW_ACTION")
    translation["status"] = next_status
    if translation.get("requires_legal_review") and reviewer["reviewer_role"] == "LEGAL_REVIEWER" and next_status == "APPROVED":
        translation["legal_review_status"] = "APPROVED"
    translation["updated_at"] = _now()
    review = {
        "review_id": _new_id("TRV"),
        "translation_key_id": translation_key_id,
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer["reviewer_role"],
        "review_action": review_action,
        "from_status": previous,
        "to_status": next_status,
        "comment": comment,
        "created_at": _now(),
    }
    save_translation_key(translation)
    save_translation_review(review)
    return {"status": next_status, "translation": translation, "review": review}


def approve_translation(translation_key_id: str, reviewer_id: str, publish: bool = False) -> dict[str, Any]:
    result = submit_translation_review(
        translation_key_id=translation_key_id,
        reviewer_id=reviewer_id,
        review_action="APPROVED",
        comment="Approved through localization review workflow.",
    )
    if publish:
        translation = result["translation"]
        reviewer = get_language_reviewer(reviewer_id)
        if not reviewer or not reviewer_can_publish(reviewer, translation):
            raise PermissionError("PUBLISH_REQUIRES_AUTHORIZED_REVIEWER")
        if translation.get("requires_legal_review") and translation.get("legal_review_status") != "APPROVED":
            raise PermissionError("PUBLISH_REQUIRES_LEGAL_REVIEW")
        translation["status"] = "PUBLISHED"
        translation["published_at"] = _now()
        save_translation_key(translation)
        result["status"] = "PUBLISHED"
    return result


def reject_translation(translation_key_id: str, reviewer_id: str, reason: str = "") -> dict[str, Any]:
    return submit_translation_review(
        translation_key_id=translation_key_id,
        reviewer_id=reviewer_id,
        review_action="REJECTED",
        comment=reason or "Rejected by localization reviewer.",
    )


def language_status(language_code: str) -> dict[str, Any]:
    seed_core_translation_keys()
    items = list_translation_keys(language_code)
    counts = Counter(item["status"] for item in items)
    approved = sum(1 for item in items if item["status"] in {"APPROVED", "PUBLISHED"})
    total = len(items)
    legal_items = [item for item in items if item.get("requires_legal_review")]
    legal_approved = sum(1 for item in legal_items if item.get("legal_review_status") == "APPROVED")
    return {
        "language_code": language_code,
        "total_keys": total,
        "status_counts": dict(counts),
        "approved_or_published_count": approved,
        "coverage_pct": round((approved / total * 100), 2) if total else 0,
        "legal_review_required_count": len(legal_items),
        "legal_review_approved_count": legal_approved,
        "production_ready": total > 0 and approved == total and legal_approved == len(legal_items),
        "fallback_language": "en-US",
        "exposure_rule": "Translations not APPROVED or PUBLISHED are hidden from production UI.",
    }


def resolve_translation(key_name: str, language_code: str) -> dict[str, Any]:
    seed_core_translation_keys()
    item = find_translation_key(key_name, language_code)
    if item and item["status"] in {"APPROVED", "PUBLISHED"}:
        return {"key_name": key_name, "language_code": language_code, "text": item["translated_text"], "source": "APPROVED"}
    fallback = find_translation_key(key_name, "en-US")
    if fallback and fallback["status"] in {"APPROVED", "PUBLISHED"}:
        return {"key_name": key_name, "language_code": language_code, "text": fallback["translated_text"], "source": "FALLBACK_EN_US"}
    return {"key_name": key_name, "language_code": language_code, "text": key_name, "source": "KEY_NAME_FALLBACK"}


def review_history(translation_key_id: str) -> dict[str, Any]:
    return {"translation_key_id": translation_key_id, "items": list_translation_reviews(translation_key_id)}
