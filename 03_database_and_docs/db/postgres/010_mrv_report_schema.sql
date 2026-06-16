-- ZENOV Annual Carbon MRV Report Schema V1
-- Reports are immutable snapshots. Later data changes must not mutate prior reports.

CREATE TABLE IF NOT EXISTS mrv_reports (
  report_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  owner_entity TEXT NOT NULL,
  report_period_start DATE NOT NULL,
  report_period_end DATE NOT NULL,
  methodology_id TEXT,
  methodology_version TEXT,
  packet_count INTEGER NOT NULL DEFAULT 0,
  evidence_count INTEGER NOT NULL DEFAULT 0,
  mrv_count INTEGER NOT NULL DEFAULT 0,
  asset_candidate_count INTEGER NOT NULL DEFAULT 0,
  total_distance_km NUMERIC NOT NULL DEFAULT 0,
  total_revenue NUMERIC NOT NULL DEFAULT 0,
  baseline_emission_kgco2e NUMERIC NOT NULL DEFAULT 0,
  project_emission_kgco2e NUMERIC NOT NULL DEFAULT 0,
  reduction_kgco2e NUMERIC NOT NULL DEFAULT 0,
  reduction_tco2e NUMERIC NOT NULL DEFAULT 0,
  estimated_value_krw NUMERIC NOT NULL DEFAULT 0,
  estimated_value_usd NUMERIC NOT NULL DEFAULT 0,
  verification_score NUMERIC(5,2),
  verification_status TEXT NOT NULL DEFAULT 'PENDING',
  registry_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  report_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  report_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'GENERATED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mrv_reports_owner_entity
  ON mrv_reports(owner_entity);

CREATE INDEX IF NOT EXISTS idx_mrv_reports_period
  ON mrv_reports(report_period_start, report_period_end);

CREATE INDEX IF NOT EXISTS idx_mrv_reports_status
  ON mrv_reports(status);
