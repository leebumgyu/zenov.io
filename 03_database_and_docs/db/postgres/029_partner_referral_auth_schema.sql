-- ZENOV Partner / Referral Auth + Role Permission Schema
-- Goal: separate company-level Partner Code authentication from individual Referral Code authentication.

CREATE TABLE IF NOT EXISTS partner_auth_accounts (
  partner_code TEXT PRIMARY KEY,
  partner_name TEXT NOT NULL,
  tenant_id TEXT,
  sub_unit_code TEXT,
  contract_status TEXT NOT NULL DEFAULT 'ACTIVE',
  role TEXT NOT NULL,
  access_password_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  failed_login_count INTEGER NOT NULL DEFAULT 0,
  locked_at TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (role IN ('PARTNER_ADMIN', 'PARTNER_MANAGER', 'PARTNER_READ_ONLY', 'PARTNER_FINANCE')),
  CHECK (status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'SUSPENDED', 'DISABLED'))
);

CREATE TABLE IF NOT EXISTS referral_auth_accounts (
  referral_code TEXT PRIMARY KEY,
  owner_type TEXT NOT NULL,
  owner_name TEXT NOT NULL,
  linked_partner_code TEXT,
  linked_sub_unit_code TEXT,
  reward_policy_id TEXT NOT NULL,
  role TEXT NOT NULL,
  access_password_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  failed_login_count INTEGER NOT NULL DEFAULT 0,
  locked_at TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (role IN ('REFERRAL_OWNER', 'REFERRAL_AGENT', 'REFERRAL_READ_ONLY')),
  CHECK (status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'SUSPENDED', 'DISABLED'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
  session_id TEXT PRIMARY KEY,
  access_token_hash TEXT NOT NULL,
  account_type TEXT NOT NULL,
  subject_code TEXT NOT NULL,
  role TEXT NOT NULL,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  CHECK (account_type IN ('PARTNER', 'REFERRAL'))
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
  reset_id TEXT PRIMARY KEY,
  reset_token_hash TEXT NOT NULL,
  account_type TEXT NOT NULL,
  subject_code TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  CHECK (account_type IN ('PARTNER', 'REFERRAL')),
  CHECK (status IN ('ACTIVE', 'USED', 'EXPIRED', 'REVOKED'))
);

CREATE TABLE IF NOT EXISTS auth_audit_logs (
  auth_audit_id TEXT PRIMARY KEY,
  account_type TEXT NOT NULL,
  subject_code TEXT NOT NULL,
  event_type TEXT NOT NULL,
  event_status TEXT NOT NULL,
  message TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'system',
  detail JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partner_auth_role_status
  ON partner_auth_accounts(role, status);

CREATE INDEX IF NOT EXISTS idx_referral_auth_role_status
  ON referral_auth_accounts(role, status);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_subject
  ON auth_sessions(account_type, subject_code, expires_at DESC);

CREATE INDEX IF NOT EXISTS idx_auth_audit_subject
  ON auth_audit_logs(account_type, subject_code, created_at DESC);

-- Security rules:
-- 1. Store access_password_hash only. Never store plaintext passwords.
-- 2. Partner Code identifies companies/institutions; Referral Code identifies individuals/events.
-- 3. Referral accounts cannot access Partner Admin APIs.
-- 4. Five failed login attempts must lock the account until admin or password reset recovery.
