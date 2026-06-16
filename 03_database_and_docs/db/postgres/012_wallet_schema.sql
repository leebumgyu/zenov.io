-- ZENOV Green Point & Wallet Schema V1
-- Points are not a game reward. They are a reward ledger linked to verified carbon asset candidates.

CREATE TABLE IF NOT EXISTS driver_wallets (
  wallet_id TEXT PRIMARY KEY,
  driver_id TEXT NOT NULL UNIQUE,
  owner_entity TEXT NOT NULL,
  balance_points NUMERIC NOT NULL DEFAULT 0,
  total_earned_points NUMERIC NOT NULL DEFAULT 0,
  total_redeemed_points NUMERIC NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wallet_transactions (
  transaction_id TEXT PRIMARY KEY,
  wallet_id TEXT NOT NULL REFERENCES driver_wallets(wallet_id),
  driver_id TEXT NOT NULL,
  transaction_type TEXT NOT NULL,
  point_amount NUMERIC NOT NULL,
  balance_after NUMERIC NOT NULL,
  asset_id TEXT NOT NULL,
  asset_serial_number TEXT,
  packet_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  mrv_id TEXT NOT NULL,
  verification_id TEXT NOT NULL,
  source_vehicle_id TEXT,
  reduction_kgco2e NUMERIC NOT NULL DEFAULT 0,
  reward_policy_id TEXT NOT NULL,
  reward_policy_version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'POSTED',
  trace_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_driver_id
  ON wallet_transactions(driver_id);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_asset_id
  ON wallet_transactions(asset_id);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_packet_id
  ON wallet_transactions(packet_id);
