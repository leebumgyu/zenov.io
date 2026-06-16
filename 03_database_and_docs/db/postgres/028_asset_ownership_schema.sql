-- ZENOV Sprint 24 - Global Asset Ownership & Custody Engine
-- Carbon Asset Candidate is not a Carbon Credit. This schema tracks ownership,
-- custody, and transfer history for verified MRV asset packages.

CREATE TABLE IF NOT EXISTS asset_ownership_records (
    ownership_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL UNIQUE,
    serial_number TEXT,
    owner_entity TEXT NOT NULL,
    owner_type TEXT NOT NULL,
    owner_country TEXT,
    custodian_entity TEXT NOT NULL,
    custodian_type TEXT NOT NULL,
    custody_status TEXT NOT NULL DEFAULT 'HELD',
    ownership_status TEXT NOT NULL DEFAULT 'ACTIVE',
    acquired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retired_at TIMESTAMPTZ,
    asset_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS asset_custody_records (
    custody_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    custodian_entity TEXT NOT NULL,
    custodian_type TEXT NOT NULL,
    custody_scope TEXT NOT NULL DEFAULT 'REGISTRY_PREPARATION',
    custody_status TEXT NOT NULL DEFAULT 'HELD',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    custody_terms JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS asset_transfer_records (
    transfer_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    from_owner_entity TEXT NOT NULL,
    from_owner_type TEXT NOT NULL,
    to_owner_entity TEXT NOT NULL,
    to_owner_type TEXT NOT NULL,
    transfer_reason TEXT NOT NULL,
    transfer_status TEXT NOT NULL DEFAULT 'COMPLETED',
    transfer_reference TEXT,
    transferred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor TEXT NOT NULL DEFAULT 'system',
    pre_transfer_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    post_transfer_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS asset_ownership_audit_logs (
    ownership_audit_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_status TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'system',
    message TEXT NOT NULL,
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_ownership_owner
    ON asset_ownership_records (owner_entity, owner_type);

CREATE INDEX IF NOT EXISTS idx_asset_transfer_asset
    ON asset_transfer_records (asset_id, transferred_at DESC);

CREATE INDEX IF NOT EXISTS idx_asset_ownership_audit_asset
    ON asset_ownership_audit_logs (asset_id, created_at DESC);
