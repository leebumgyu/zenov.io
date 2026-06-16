from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import (
    customer_health_snapshots,
    onboarding_checklists,
    onboarding_projects,
    save_customer_health_snapshot_memory,
    save_onboarding_checklist_memory,
    save_onboarding_project_memory,
)
from .deployment_service import create_deployment_run, list_deployment_runs
from .deployment_template_engine import get_deployment_template, list_deployment_templates
from .onboarding_checklist import checklist_progress, create_default_checklist


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _now() -> str:
    return _now_dt().isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _target(start: datetime, days: int) -> str:
    return (start + timedelta(days=days)).isoformat()


def _project_checklist(onboarding_id: str) -> list[dict[str, Any]]:
    return sorted(
        [item for item in onboarding_checklists.values() if item.get("onboarding_id") == onboarding_id],
        key=lambda item: int(item.get("target_day", 0)),
    )


def _health_from_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    progress = checklist_progress(items)
    completed = progress["completed_milestones"]
    score = min(100.0, round(20 + completed * 16, 2))
    if completed >= 3:
        status = "GREEN"
    elif completed >= 1:
        status = "YELLOW"
    else:
        status = "YELLOW"
    if any(item.get("status") == "BLOCKED" for item in items):
        status = "RED"
        score = min(score, 45.0)
    return {
        "health_score": score,
        "health_status": status,
        **progress,
    }


def start_onboarding(
    *,
    customer_name: str,
    industry_type: str = "TAXI",
    tenant_id: Optional[str] = None,
    partner_id: Optional[str] = None,
    template_id: Optional[str] = None,
) -> dict[str, Any]:
    template = get_deployment_template(template_id) if template_id else None
    if not template:
        templates = list_deployment_templates(industry_type.upper())
        if not templates:
            raise ValueError("NO_TEMPLATE_FOR_INDUSTRY")
        template = templates[0]
    started_at = _now_dt()
    onboarding_id = _new_id("ONB")
    project = {
        "onboarding_id": onboarding_id,
        "tenant_id": tenant_id,
        "partner_id": partner_id,
        "customer_name": customer_name,
        "industry_type": industry_type.upper(),
        "template_id": template["template_id"],
        "lifecycle_status": "ONBOARDING",
        "health_score": 20.0,
        "health_status": "YELLOW",
        "started_at": started_at.isoformat(),
        "target_first_data_at": _target(started_at, 1),
        "target_first_evidence_at": _target(started_at, 7),
        "target_first_mrv_at": _target(started_at, 30),
        "target_verification_at": _target(started_at, 60),
        "target_first_asset_at": _target(started_at, 90),
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_onboarding_project_memory(project)
    checklist = create_default_checklist(onboarding_id)
    deployment = create_deployment_run(onboarding_id, template["template_id"])
    return {
        "status": "ONBOARDING_STARTED",
        "project": project,
        "template": template,
        "checklist": checklist,
        "deployment": deployment,
        "success_path": "Day 1 data connection -> Day 7 evidence -> Day 30 MRV -> Day 60 verification -> Day 90 asset",
    }


def complete_milestone(
    *,
    onboarding_id: str,
    milestone_key: str,
    evidence_ref: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    items = _project_checklist(onboarding_id)
    if not items:
        raise ValueError("ONBOARDING_NOT_FOUND")
    matched = None
    for item in items:
        if item.get("milestone_key") == milestone_key:
            matched = item
            break
    if not matched:
        raise ValueError("MILESTONE_NOT_FOUND")
    matched["status"] = "COMPLETED"
    matched["completed_at"] = _now()
    matched["evidence_ref"] = evidence_ref
    matched["notes"] = notes
    matched["updated_at"] = _now()
    save_onboarding_checklist_memory(matched)
    return customer_success_dashboard(onboarding_id)


def create_health_snapshot(onboarding_id: str) -> dict[str, Any]:
    dashboard = customer_success_dashboard(onboarding_id)
    if dashboard.get("status") == "NOT_FOUND":
        raise ValueError("ONBOARDING_NOT_FOUND")
    metrics = dashboard["metrics"]
    snapshot = {
        "health_snapshot_id": _new_id("CSH"),
        "onboarding_id": onboarding_id,
        "health_score": metrics["health_score"],
        "health_status": metrics["health_status"],
        "time_to_onboard_days": metrics.get("time_to_onboard_days"),
        "time_to_first_evidence_days": metrics.get("time_to_first_evidence_days"),
        "time_to_first_mrv_days": metrics.get("time_to_first_mrv_days"),
        "time_to_first_asset_days": metrics.get("time_to_first_asset_days"),
        "retention_risk": dashboard["retention_risk"],
        "snapshot": dashboard,
        "created_at": _now(),
    }
    save_customer_health_snapshot_memory(snapshot)
    return snapshot


def _duration_days(project: dict[str, Any], item: Optional[dict[str, Any]]) -> Optional[float]:
    if not item or not item.get("completed_at"):
        return None
    start = datetime.fromisoformat(project["started_at"])
    completed = datetime.fromisoformat(item["completed_at"])
    return round((completed - start).total_seconds() / 86400, 2)


def customer_success_dashboard(onboarding_id: str) -> dict[str, Any]:
    project = onboarding_projects.get(onboarding_id)
    if not project:
        return {"status": "NOT_FOUND", "onboarding_id": onboarding_id}
    checklist = _project_checklist(onboarding_id)
    health = _health_from_items(checklist)
    by_key = {item["milestone_key"]: item for item in checklist}
    metrics = {
        **health,
        "time_to_onboard_days": _duration_days(project, by_key.get("DAY_1_DATA_CONNECTION")),
        "time_to_first_evidence_days": _duration_days(project, by_key.get("DAY_7_FIRST_EVIDENCE")),
        "time_to_first_mrv_days": _duration_days(project, by_key.get("DAY_30_FIRST_MRV")),
        "time_to_first_asset_days": _duration_days(project, by_key.get("DAY_90_FIRST_ASSET")),
        "customer_retention_rate": 0.95 if health["health_status"] == "GREEN" else 0.78 if health["health_status"] == "YELLOW" else 0.45,
    }
    project["health_score"] = health["health_score"]
    project["health_status"] = health["health_status"]
    project["updated_at"] = _now()
    save_onboarding_project_memory(project)
    retention_risk = "LOW" if health["health_status"] == "GREEN" else "MEDIUM" if health["health_status"] == "YELLOW" else "HIGH"
    return {
        "status": "OK",
        "project": project,
        "metrics": metrics,
        "retention_risk": retention_risk,
        "checklist": checklist,
        "deployment_runs": list_deployment_runs(onboarding_id),
        "latest_health_snapshot": list(customer_health_snapshots.values())[-1] if customer_health_snapshots else None,
    }


def list_customer_success_projects() -> dict[str, Any]:
    projects = list(onboarding_projects.values())
    return {
        "count": len(projects),
        "green": sum(1 for item in projects if item.get("health_status") == "GREEN"),
        "yellow": sum(1 for item in projects if item.get("health_status") == "YELLOW"),
        "red": sum(1 for item in projects if item.get("health_status") == "RED"),
        "items": sorted(projects, key=lambda item: item.get("created_at", ""), reverse=True),
    }
