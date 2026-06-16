-- ZENOV MRV & Carbon Value Engine PostgreSQL Schema V1

CREATE TABLE IF NOT EXISTS mrv_results (
  mrv_id TEXT PRIMARY KEY,
  packet_id TEXT NOT NULL REFERENCES trust_packets(packet_id) ON DELETE CASCADE,
  source_id TEXT NOT NULL,
  co2e_kg DOUBLE PRECISION NOT NULL,
  co2e_ton DOUBLE PRECISION NOT NULL,
  methodology_version TEXT NOT NULL,
  emission_factor_version TEXT NOT NULL,
  calculation_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'SUCCESS',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mrv_results_packet_id
  ON mrv_results (packet_id);

CREATE INDEX IF NOT EXISTS idx_mrv_results_source_id
  ON mrv_results (source_id);

CREATE TABLE IF NOT EXISTS carbon_value_results (
  value_id TEXT PRIMARY KEY,
  mrv_id TEXT NOT NULL REFERENCES mrv_results(mrv_id) ON DELETE CASCADE,
  packet_id TEXT NOT NULL REFERENCES trust_packets(packet_id) ON DELETE CASCADE,
  carbon_price_per_ton DOUBLE PRECISION NOT NULL,
  currency TEXT NOT NULL,
  price_source TEXT NOT NULL,
  price_date DATE NOT NULL,
  estimated_value DOUBLE PRECISION NOT NULL,
  value_engine_version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'SUCCESS',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_carbon_value_results_mrv_id
  ON carbon_value_results (mrv_id);

CREATE INDEX IF NOT EXISTS idx_carbon_value_results_packet_id
  ON carbon_value_results (packet_id);
