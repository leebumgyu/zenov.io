-- ZENOV SPRINT 17 - CUSTOMER SUCCESS & DEPLOYMENT AUTOMATION
-- Purpose: reduce new customer onboarding time and track first evidence, MRV, verification, and asset milestones.

CREATE TABLE IF NOT EXISTS onboarding_projects (
    onboarding_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    partner_id TEXT,
    customer_name TEXT NOT NULL,
    industry_type TEXT NOT NULL,
    template_id TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'ONBOARDING',
    health_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    health_status TEXT NOT NULL DEFAULT 'YELLOW',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target_first_data_at TIMESTAMPTZ,
    target_first_evidence_at TIMESTAMPTZ,
    target_first_mrv_at TIMESTAMPTZ,
    target_verification_at TIMESTAMPTZ,
    target_first_asset_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS onboarding_checklists (
    checklist_id TEXT PRIMARY KEY,
    onboarding_id TEXT NOT NULL REFERENCES onboarding_projects(onboarding_id),
    milestone_key TEXT NOT NULL,
    milestone_name TEXT NOT NULL,
    target_day INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    completed_at TIMESTAMPTZ,
    evidence_ref TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deployment_templates (
    template_id TEXT PRIMARY KEY,
    industry_type TEXT NOT NULL,
    template_name TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    supported_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    validation_rules JSONB NOT NULL DEFAULT '[]'::jsonb,
    default_mapping JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deployment_runs (
    deployment_run_id TEXT PRIMARY KEY,
    onboarding_id TEXT NOT NULL REFERENCES onboarding_projects(onboarding_id),
    template_id TEXT NOT NULL,
    run_status TEXT NOT NULL DEFAULT 'PENDING',
    connector_status TEXT NOT NULL DEFAULT 'NOT_CONFIGURED',
    data_validation_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
    first_asset_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
    run_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS customer_health_snapshots (
    health_snapshot_id TEXT PRIMARY KEY,
    onboarding_id TEXT NOT NULL REFERENCES onboarding_projects(onboarding_id),
    health_score NUMERIC(5,2) NOT NULL,
    health_status TEXT NOT NULL,
    time_to_onboard_days NUMERIC(8,2),
    time_to_first_evidence_days NUMERIC(8,2),
    time_to_first_mrv_days NUMERIC(8,2),
    time_to_first_asset_days NUMERIC(8,2),
    retention_risk TEXT NOT NULL DEFAULT 'UNKNOWN',
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_onboarding_projects_tenant_id
    ON onboarding_projects(tenant_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_projects_partner_id
    ON onboarding_projects(partner_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_checklists_onboarding_id
    ON onboarding_checklists(onboarding_id);

CREATE INDEX IF NOT EXISTS idx_deployment_runs_onboarding_id
    ON deployment_runs(onboarding_id);
