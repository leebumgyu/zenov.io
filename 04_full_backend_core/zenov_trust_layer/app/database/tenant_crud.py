from __future__ import annotations

from typing import Any, Optional

from ..storage import (
    billing_accounts,
    tenant_audit_logs,
    tenant_subscriptions,
    tenant_users,
    tenants,
    save_billing_account_memory,
    save_tenant_audit_log_memory,
    save_tenant_memory,
    save_tenant_subscription_memory,
    save_tenant_user_memory,
)


def save_tenant(tenant: dict[str, Any]) -> dict[str, Any]:
    save_tenant_memory(tenant)
    return tenant


def get_tenant(tenant_id: str) -> Optional[dict[str, Any]]:
    return tenants.get(tenant_id)


def find_tenant_by_slug(slug: str) -> Optional[dict[str, Any]]:
    return next((tenant for tenant in tenants.values() if tenant.get("tenant_slug") == slug), None)


def list_tenants() -> list[dict[str, Any]]:
    return sorted(tenants.values(), key=lambda item: item.get("created_at", ""))


def save_tenant_user(user: dict[str, Any]) -> dict[str, Any]:
    save_tenant_user_memory(user)
    return user


def list_tenant_users(tenant_id: str) -> list[dict[str, Any]]:
    return [user for user in tenant_users.values() if user.get("tenant_id") == tenant_id]


def save_subscription(subscription: dict[str, Any]) -> dict[str, Any]:
    save_tenant_subscription_memory(subscription)
    return subscription


def get_tenant_subscription(tenant_id: str) -> Optional[dict[str, Any]]:
    return next((item for item in tenant_subscriptions.values() if item.get("tenant_id") == tenant_id), None)


def save_billing_account(account: dict[str, Any]) -> dict[str, Any]:
    save_billing_account_memory(account)
    return account


def get_billing_account(tenant_id: str) -> Optional[dict[str, Any]]:
    return next((item for item in billing_accounts.values() if item.get("tenant_id") == tenant_id), None)


def save_tenant_audit_log(log: dict[str, Any]) -> dict[str, Any]:
    save_tenant_audit_log_memory(log)
    return log


def get_tenant_audit_logs(tenant_id: str) -> list[dict[str, Any]]:
    return [log for log in tenant_audit_logs if log.get("tenant_id") == tenant_id]
