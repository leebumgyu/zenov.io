-- ZENOV SPRINT 18 - PRODUCTION READINESS & CUSTOMER SUCCESS
-- Scope: operational readiness, SLA monitoring, runbook tracking, and customer success KPIs.

CREATE TABLE IF NOT EXISTS production_readiness_checks (
    check_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    category TEXT NOT NULL,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    severity TEXT NOT NULL DEFAULT 'MEDIUM',
    evidence_ref TEXT,
    owner_role TEXT NOT NULL DEFAULT 'SUPER_ADMIN',
    checked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sla_snapshots (
    sla_snapshot_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    data_collection_success_rate NUMERIC(8,4) NOT NULL,
    api_response_time_ms NUMERIC(12,2) NOT NULL,
    import_success_rate NUMERIC(8,4) NOT NULL,
    verification_success_rate NUMERIC(8,4) NOT NULL,
    sla_status TEXT NOT NULL,
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operational_runbooks (
    runbook_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    runbook_type TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'MEDIUM',
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    owner_role TEXT NOT NULL DEFAULT 'OPERATIONS',
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_production_readiness_tenant
    ON production_readiness_checks(tenant_id);

CREATE INDEX IF NOT EXISTS idx_sla_snapshots_tenant
    ON sla_snapshots(tenant_id);

CREATE INDEX IF NOT EXISTS idx_operational_runbooks_tenant
    ON operational_runbooks(tenant_id);
