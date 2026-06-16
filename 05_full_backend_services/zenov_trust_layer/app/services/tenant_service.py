from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..database.tenant_crud import (
    find_tenant_by_slug,
    get_tenant,
    get_tenant_audit_logs,
    list_tenant_users,
    list_tenants,
    save_tenant,
    save_tenant_audit_log,
    save_tenant_user,
)
from ..storage import (
    carbon_asset_candidates,
    driver_wallets,
    import_jobs,
    mrv_reports,
    wallet_transactions,
)
from .billing_service import billing_summary, create_billing_account
from .kpi_service import portfolio_kpi
from .subscription_service import create_subscription, get_subscription


ROLES = {"SUPER_ADMIN", "PARTNER_ADMIN", "FLEET_MANAGER", "DRIVER", "AUDITOR"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _slug(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def _tenant_audit(tenant_id: str, event_type: str, message: str, actor: str = "system", detail: Optional[dict[str, Any]] = None) -> None:
    save_tenant_audit_log(
        {
            "tenant_audit_id": _new_id("TAUD"),
            "tenant_id": tenant_id,
            "event_type": event_type,
            "message": message,
            "actor": actor,
            "detail": detail or {},
            "created_at": _now(),
        }
    )


def create_tenant(
    *,
    tenant_name: str,
    tenant_slug: Optional[str] = None,
    tenant_type: str = "TAXI_COMPANY",
    subscription_plan: str = "PILOT",
    admin_email: Optional[str] = None,
    status: str = "ACTIVE",
) -> dict[str, Any]:
    slug = _slug(tenant_slug or tenant_name)
    existing = find_tenant_by_slug(slug)
    if existing:
        return {
            "status": "EXISTS",
            "tenant": existing,
            "subscription": get_subscription(existing["tenant_id"]),
            "billing": billing_summary(existing["tenant_id"]),
        }
    tenant_id = _new_id("TNT")
    tenant = {
        "tenant_id": tenant_id,
        "tenant_slug": slug,
        "tenant_name": tenant_name,
        "tenant_type": tenant_type,
        "status": status,
        "subscription_plan": subscription_plan.upper(),
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_tenant(tenant)
    admin = {
        "user_id": _new_id("TUSR"),
        "tenant_id": tenant_id,
        "role": "PARTNER_ADMIN",
        "email": admin_email,
        "display_name": f"{tenant_name} Admin",
        "status": "ACTIVE",
        "created_at": _now(),
    }
    save_tenant_user(admin)
    subscription = create_subscription(tenant_id, subscription_plan)
    billing = create_billing_account(tenant_id, admin_email)
    _tenant_audit(tenant_id, "TENANT_CREATED", "Tenant created without DB reconstruction.", detail={"subscription_plan": subscription_plan})
    return {
        "status": "CREATED",
        "tenant": tenant,
        "admin_user": admin,
        "subscription": subscription,
        "billing": billing,
        "rule": "A new company can onboard by creating a tenant, not by rebuilding the database.",
    }


def resolve_tenant(identifier: str) -> Optional[dict[str, Any]]:
    return get_tenant(identifier) or find_tenant_by_slug(identifier)


def tenant_access_check(tenant_id: str, role: str) -> dict[str, Any]:
    tenant = resolve_tenant(tenant_id)
    if not tenant:
        return {"allowed": False, "reason": "TENANT_NOT_FOUND"}
    if role not in ROLES:
        return {"allowed": False, "reason": "ROLE_NOT_SUPPORTED", "supported_roles": sorted(ROLES)}
    if tenant.get("status") == "SUSPENDED" and role != "SUPER_ADMIN":
        return {"allowed": False, "reason": "TENANT_SUSPENDED"}
    return {"allowed": True, "tenant": tenant, "role": role}


def _tenant_owner_keys(tenant: dict[str, Any]) -> set[str]:
    return {
        tenant["tenant_id"],
        tenant["tenant_slug"].upper().replace("-", "_"),
        tenant["tenant_slug"],
        tenant["tenant_name"],
    }


def tenant_dashboard(tenant_id: str) -> dict[str, Any]:
    tenant = resolve_tenant(tenant_id)
    if not tenant:
        return {"status": "NOT_FOUND", "tenant_id": tenant_id}
    owner_keys = _tenant_owner_keys(tenant)
    assets = [
        item for item in carbon_asset_candidates.values()
        if str(item.get("owner_entity")) in owner_keys
    ]
    wallets = [
        wallet for wallet in driver_wallets.values()
        if str(wallet.get("owner_entity")) in owner_keys
    ]
    transactions = [
        tx for tx in wallet_transactions.values()
        if str(tx.get("owner_entity")) in owner_keys
    ]
    reports = [
        report for report in mrv_reports.values()
        if str(report.get("owner_entity")) in owner_keys
    ]
    jobs = [
        job for job in import_jobs.values()
        if str(job.get("company_id")) in owner_keys
    ]
    portfolio_id = tenant["tenant_slug"].upper().replace("-", "_")
    if not assets and portfolio_id != tenant_id:
        portfolio = portfolio_kpi(portfolio_id)
    else:
        portfolio = {
            "current": {
                "fleet_size": len({item.get("vehicle_id") for item in assets if item.get("vehicle_id")}),
                "verified_reduction_tco2e": round(sum(float(item.get("issued_quantity_tco2e", 0) or 0) for item in assets), 6),
                "asset_count": len(assets),
                "registry_count": sum(1 for item in assets if item.get("registry_status") in {"SUBMITTED", "REGISTERED", "RETIRED"}),
                "portfolio_value_krw": round(sum(float(item.get("estimated_value_krw", 0) or 0) for item in assets), 2),
            }
        }
    return {
        "status": "OK",
        "tenant": tenant,
        "isolation": {
            "asset_count": len(assets),
            "wallet_count": len(wallets),
            "wallet_transaction_count": len(transactions),
            "registry_asset_count": sum(1 for item in assets if item.get("registry_status") in {"SUBMITTED", "REGISTERED", "RETIRED"}),
            "report_count": len(reports),
            "import_job_count": len(jobs),
        },
        "subscription": get_subscription(tenant["tenant_id"]),
        "billing": billing_summary(tenant["tenant_id"]),
        "portfolio": portfolio,
        "users": list_tenant_users(tenant["tenant_id"]),
        "audit_logs": get_tenant_audit_logs(tenant["tenant_id"])[-20:],
    }


def tenant_list_view() -> dict[str, Any]:
    items = list_tenants()
    return {
        "count": len(items),
        "items": items,
        "roles": sorted(ROLES),
        "message": "Zenov is a multi-tenant SaaS platform, not a single-project deployment.",
    }
