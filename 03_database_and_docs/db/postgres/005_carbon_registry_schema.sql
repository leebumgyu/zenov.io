-- ZENOV Carbon Registry Schema V1
-- Carbon Registry is the next layer after packet -> evidence -> mrv -> value.

CREATE TABLE IF NOT EXISTS carbon_projects (
  carbon_project_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  owner_name TEXT,
  source_type TEXT NOT NULL,
  start_date DATE,
  status TEXT NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS carbon_assets (
  asset_id TEXT PRIMARY KEY,
  carbon_project_id TEXT REFERENCES carbon_projects(carbon_project_id),
  packet_id TEXT REFERENCES trust_packets(packet_id),
  evidence_id TEXT REFERENCES digital_evidence(evidence_id),
  mrv_id TEXT REFERENCES mrv_results(mrv_id),
  value_id TEXT REFERENCES carbon_value_results(value_id),
  co2e_ton NUMERIC(18,6),
  estimated_value NUMERIC(18,2),
  currency TEXT NOT NULL DEFAULT 'KRW',
  status TEXT NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  verified_at TIMESTAMPTZ,
  retired_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_carbon_assets_evidence_id
  ON carbon_assets(evidence_id);

CREATE INDEX IF NOT EXISTS idx_carbon_assets_mrv_id
  ON carbon_assets(mrv_id);

CREATE INDEX IF NOT EXISTS idx_carbon_assets_value_id
  ON carbon_assets(value_id);

CREATE INDEX IF NOT EXISTS idx_carbon_assets_status
  ON carbon_assets(status);

