-- ZENOV Commercial Readiness & Multi-Tenant Platform Schema
-- Goal: onboard many taxi, bus, logistics, and energy companies without DB reconstruction.

CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  tenant_slug TEXT NOT NULL UNIQUE,
  tenant_name TEXT NOT NULL,
  tenant_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  subscription_plan TEXT NOT NULL DEFAULT 'PILOT',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (status IN ('ACTIVE', 'SUSPENDED', 'ARCHIVED')),
  CHECK (subscription_plan IN ('FREE', 'PILOT', 'ENTERPRISE', 'GOVERNMENT'))
);

CREATE TABLE IF NOT EXISTS tenant_users (
  user_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  role TEXT NOT NULL,
  email TEXT,
  display_name TEXT,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (role IN ('SUPER_ADMIN', 'PARTNER_ADMIN', 'FLEET_MANAGER', 'DRIVER', 'AUDITOR'))
);

CREATE TABLE IF NOT EXISTS tenant_subscriptions (
  subscription_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  plan TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  billing_cycle TEXT NOT NULL DEFAULT 'MONTHLY',
  monthly_fee_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
  seat_limit INTEGER NOT NULL DEFAULT 0,
  vehicle_limit INTEGER NOT NULL DEFAULT 0,
  asset_limit INTEGER NOT NULL DEFAULT 0,
  api_call_limit_monthly INTEGER NOT NULL DEFAULT 0,
  retention_days INTEGER NOT NULL DEFAULT 30,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  trial_ends_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS billing_accounts (
  billing_account_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  billing_email TEXT,
  currency TEXT NOT NULL DEFAULT 'KRW',
  payment_status TEXT NOT NULL DEFAULT 'TRIAL',
  current_balance_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
  monthly_fee_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tenant_audit_logs (
  tenant_audit_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  event_type TEXT NOT NULL,
  message TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'system',
  detail JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tenant isolation extension points:
-- Every operational table should carry a tenant_id or an owner_entity that maps to a tenant.
-- This Sprint keeps legacy owner_entity compatibility while adding tenant-level SaaS controls.

CREATE INDEX IF NOT EXISTS idx_tenants_slug
  ON tenants(tenant_slug);

CREATE INDEX IF NOT EXISTS idx_tenant_users_tenant_role
  ON tenant_users(tenant_id, role);

CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_tenant
  ON tenant_subscriptions(tenant_id, plan, status);

CREATE INDEX IF NOT EXISTS idx_billing_accounts_tenant
  ON billing_accounts(tenant_id);

CREATE INDEX IF NOT EXISTS idx_tenant_audit_logs_tenant
  ON tenant_audit_logs(tenant_id, created_at DESC);
