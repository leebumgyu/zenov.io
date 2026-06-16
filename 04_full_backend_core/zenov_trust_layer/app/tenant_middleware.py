from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .services.tenant_service import resolve_tenant


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Attach optional tenant context to each request.

    The current demo remains permissive so legacy endpoints keep working.
    Tenant-aware routes can inspect request.state.tenant_context and enforce
    isolation/RBAC explicitly.
    """

    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("x-tenant-id") or request.headers.get("x-tenant-slug")
        user_role = request.headers.get("x-user-role", "SUPER_ADMIN")
        tenant = resolve_tenant(tenant_id) if tenant_id else None
        request.state.tenant_context = {
            "tenant_id": tenant.get("tenant_id") if tenant else tenant_id,
            "tenant_slug": tenant.get("tenant_slug") if tenant else None,
            "tenant": tenant,
            "role": user_role,
            "is_tenant_scoped": bool(tenant),
        }
        return await call_next(request)
