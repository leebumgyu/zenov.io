from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..storage import deployment_runs, save_deployment_run_memory
from .deployment_template_engine import get_deployment_template


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def create_deployment_run(onboarding_id: str, template_id: str) -> dict[str, Any]:
    template = get_deployment_template(template_id)
    if not template:
        raise ValueError("DEPLOYMENT_TEMPLATE_NOT_FOUND")
    run = {
        "deployment_run_id": _new_id("DPLY"),
        "onboarding_id": onboarding_id,
        "template_id": template_id,
        "run_status": "READY",
        "connector_status": "AUTO_CONFIGURED",
        "data_validation_status": "CHECKLIST_READY",
        "first_asset_status": "NOT_STARTED",
        "run_snapshot": {
            "template": template,
            "message": "Connector configuration generated from template. No code change required.",
        },
        "created_at": _now(),
        "completed_at": None,
    }
    save_deployment_run_memory(run)
    return run


def list_deployment_runs(onboarding_id: str | None = None) -> list[dict[str, Any]]:
    items = list(deployment_runs.values())
    if onboarding_id:
        items = [item for item in items if item.get("onboarding_id") == onboarding_id]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)
