-- ZENOV Portfolio KPI & Target Management Schema
-- Sprint 11 target: every portfolio KPI must show current, target, achievement, and trend.

CREATE TABLE IF NOT EXISTS portfolio_targets (
  portfolio_id TEXT PRIMARY KEY,
  target_vehicle_count INTEGER NOT NULL DEFAULT 0,
  target_reduction_tco2e NUMERIC(18,6) NOT NULL DEFAULT 0,
  target_asset_count INTEGER NOT NULL DEFAULT 0,
  target_registry_count INTEGER NOT NULL DEFAULT 0,
  target_portfolio_value NUMERIC(18,2) NOT NULL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'KRW',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio_kpi_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolio_targets(portfolio_id),
  snapshot_period TEXT NOT NULL,
  snapshot_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_kpi_snapshots_portfolio
  ON portfolio_kpi_snapshots(portfolio_id, snapshot_period, created_at DESC);
