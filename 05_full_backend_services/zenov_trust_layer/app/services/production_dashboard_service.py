from __future__ import annotations

from typing import Any, Optional

from ..storage import carbon_asset_candidates, digital_evidence, mrv_reports, taxi_mrv_results
from .customer_success_service import customer_success_dashboard, list_customer_success_projects
from .production_readiness_service import list_runbooks, readiness_summary
from .sla_monitoring_service import calculate_sla_snapshot


def _latest_onboarding_id() -> Optional[str]:
    projects = list_customer_success_projects().get("items", [])
    return projects[0]["onboarding_id"] if projects else None


def production_dashboard(tenant_id: Optional[str] = "ansan-trans", onboarding_id: Optional[str] = None) -> dict[str, Any]:
    resolved_onboarding_id = onboarding_id or _latest_onboarding_id()
    customer = customer_success_dashboard(resolved_onboarding_id) if resolved_onboarding_id else {
        "status": "NO_ONBOARDING",
        "metrics": {},
        "retention_risk": "UNKNOWN",
    }
    readiness = readiness_summary(tenant_id)
    sla = calculate_sla_snapshot(tenant_id)
    runbooks = list_runbooks(tenant_id)
    firsts = {
        "first_evidence_created": bool(digital_evidence),
        "first_mrv_created": bool(taxi_mrv_results),
        "first_asset_created": bool(carbon_asset_candidates),
        "first_report_created": bool(mrv_reports),
    }
    production_status = "READY_FOR_PILOT"
    if readiness["status"] != "PRODUCTION_READY":
        production_status = "READINESS_REQUIRED"
    if customer.get("metrics", {}).get("health_status") == "RED":
        production_status = "CUSTOMER_AT_RISK"
    return {
        "tenant_id": tenant_id,
        "onboarding_id": resolved_onboarding_id,
        "production_status": production_status,
        "customer_success": customer,
        "production_readiness": readiness,
        "sla": sla,
        "runbooks": runbooks,
        "first_generation_tracker": firsts,
        "kpi": {
            "time_to_first_evidence": customer.get("metrics", {}).get("time_to_first_evidence_days"),
            "time_to_first_mrv": customer.get("metrics", {}).get("time_to_first_mrv_days"),
            "time_to_first_asset": customer.get("metrics", {}).get("time_to_first_asset_days"),
            "customer_health_score": customer.get("metrics", {}).get("health_score"),
            "retention_score": customer.get("metrics", {}).get("customer_retention_rate"),
        },
    }
