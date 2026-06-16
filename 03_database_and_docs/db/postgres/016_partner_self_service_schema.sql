-- ZENOV Partner Self-Service Dashboard Schema
-- Sprint 12 target: partners can check integration health without asking Zenov operations.

CREATE TABLE IF NOT EXISTS partner_api_keys (
  partner_id TEXT NOT NULL,
  api_key_id TEXT PRIMARY KEY,
  api_key_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_used_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS partner_health_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL,
  api_status TEXT NOT NULL,
  last_data_received_at TIMESTAMPTZ,
  upload_success_count INTEGER NOT NULL DEFAULT 0,
  upload_failed_count INTEGER NOT NULL DEFAULT 0,
  mapping_error_count INTEGER NOT NULL DEFAULT 0,
  evidence_count INTEGER NOT NULL DEFAULT 0,
  mrv_count INTEGER NOT NULL DEFAULT 0,
  verification_pass_rate NUMERIC(5,2) NOT NULL DEFAULT 0,
  asset_generated_count INTEGER NOT NULL DEFAULT 0,
  snapshot_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partner_health_partner
  ON partner_health_snapshots(partner_id, created_at DESC);
