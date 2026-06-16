-- ZENOV Methodology Governance Schema V1
-- Tracks methodology versions, immutable MRV snapshots, and change impact analysis.

CREATE TABLE IF NOT EXISTS methodologies (
  methodology_key TEXT PRIMARY KEY,
  methodology_id TEXT NOT NULL,
  version TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  effective_date DATE NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  source_reference TEXT,
  methodology_hash TEXT NOT NULL,
  config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(methodology_id, version)
);

CREATE TABLE IF NOT EXISTS methodology_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  methodology_id TEXT NOT NULL,
  methodology_version TEXT NOT NULL,
  linked_type TEXT NOT NULL,
  linked_id TEXT NOT NULL,
  snapshot_hash TEXT NOT NULL,
  snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS methodology_change_impacts (
  impact_id TEXT PRIMARY KEY,
  methodology_id TEXT NOT NULL,
  from_version TEXT NOT NULL,
  to_version TEXT NOT NULL,
  affected_mrv_count INTEGER NOT NULL DEFAULT 0,
  affected_report_count INTEGER NOT NULL DEFAULT 0,
  affected_asset_count INTEGER NOT NULL DEFAULT 0,
  baseline_factor_before NUMERIC,
  baseline_factor_after NUMERIC,
  estimated_reduction_delta_kgco2e NUMERIC NOT NULL DEFAULT 0,
  impact_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_methodologies_id_version
  ON methodologies(methodology_id, version);

CREATE INDEX IF NOT EXISTS idx_methodology_snapshots_linked
  ON methodology_snapshots(linked_type, linked_id);

CREATE INDEX IF NOT EXISTS idx_methodology_change_impacts_methodology
  ON methodology_change_impacts(methodology_id, from_version, to_version);
