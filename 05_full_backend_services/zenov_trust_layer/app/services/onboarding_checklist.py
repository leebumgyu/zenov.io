from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import save_onboarding_checklist_memory


MILESTONES = [
    ("DAY_1_DATA_CONNECTION", "Day 1 - Data Connection", 1),
    ("DAY_7_FIRST_EVIDENCE", "Day 7 - First Evidence", 7),
    ("DAY_30_FIRST_MRV", "Day 30 - First MRV", 30),
    ("DAY_60_VERIFICATION", "Day 60 - Verification Completed", 60),
    ("DAY_90_FIRST_ASSET", "Day 90 - First Asset Created", 90),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def create_default_checklist(onboarding_id: str) -> list[dict[str, Any]]:
    items = []
    for key, name, day in MILESTONES:
        item = {
            "checklist_id": _new_id("CHK"),
            "onboarding_id": onboarding_id,
            "milestone_key": key,
            "milestone_name": name,
            "target_day": day,
            "status": "PENDING",
            "completed_at": None,
            "evidence_ref": None,
            "notes": None,
            "created_at": _now(),
            "updated_at": _now(),
        }
        save_onboarding_checklist_memory(item)
        items.append(item)
    return items


def checklist_progress(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    completed = sum(1 for item in items if item.get("status") == "COMPLETED")
    rate = round((completed / total) * 100, 2) if total else 0
    return {
        "total_milestones": total,
        "completed_milestones": completed,
        "achievement_rate": rate,
    }
