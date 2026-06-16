-- ZENOV SPRINT 16 - SETTLEMENT & REVENUE ENGINE
-- Scope: settlement simulation and append-only ledger only.
-- This schema must not be interpreted as a live payment-processing system.

CREATE TABLE IF NOT EXISTS merchant_accounts (
    merchant_account_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    merchant_name TEXT NOT NULL,
    merchant_type TEXT NOT NULL,
    tenant_id TEXT,
    settlement_currency TEXT NOT NULL DEFAULT 'KRW',
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS commission_rules (
    rule_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    marketplace_fee_rate NUMERIC(8,5) NOT NULL DEFAULT 0,
    partner_fee_rate NUMERIC(8,5) NOT NULL DEFAULT 0,
    platform_fee_rate NUMERIC(8,5) NOT NULL DEFAULT 0,
    fixed_fee_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'KRW',
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    effective_date DATE NOT NULL,
    source TEXT NOT NULL DEFAULT 'ZENOV_INTERNAL_SIMULATION',
    version TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settlement_records (
    settlement_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    driver_id TEXT NOT NULL,
    wallet_transaction_id TEXT,
    offer_id TEXT NOT NULL,
    merchant_account_id TEXT NOT NULL REFERENCES merchant_accounts(merchant_account_id),
    gross_amount_krw NUMERIC(18,2) NOT NULL,
    marketplace_fee_krw NUMERIC(18,2) NOT NULL,
    partner_fee_krw NUMERIC(18,2) NOT NULL,
    platform_fee_krw NUMERIC(18,2) NOT NULL,
    fixed_fee_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
    total_fee_krw NUMERIC(18,2) NOT NULL,
    net_amount_krw NUMERIC(18,2) NOT NULL,
    point_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'PENDING',
    simulation_only BOOLEAN NOT NULL DEFAULT TRUE,
    trace_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    settled_at TIMESTAMPTZ,
    reversed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS settlement_batches (
    batch_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    batch_period TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    record_count INTEGER NOT NULL DEFAULT 0,
    total_gross_amount_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
    total_fee_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
    total_net_amount_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
    simulation_only BOOLEAN NOT NULL DEFAULT TRUE,
    record_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settlement_ledger_entries (
    ledger_entry_id TEXT PRIMARY KEY,
    settlement_id TEXT NOT NULL REFERENCES settlement_records(settlement_id),
    event_type TEXT NOT NULL,
    event_status TEXT NOT NULL,
    message TEXT,
    actor TEXT NOT NULL DEFAULT 'system',
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_settlement_records_tenant_id
    ON settlement_records(tenant_id);

CREATE INDEX IF NOT EXISTS idx_settlement_records_driver_id
    ON settlement_records(driver_id);

CREATE INDEX IF NOT EXISTS idx_settlement_records_status
    ON settlement_records(status);

CREATE INDEX IF NOT EXISTS idx_settlement_ledger_settlement_id
    ON settlement_ledger_entries(settlement_id);
