-- ZENOV Taxi Daily Operation Import Schema V1
-- CSV -> packet_id -> evidence_id -> mrv_id -> green_point

CREATE TABLE IF NOT EXISTS taxi_daily_operations (
  operation_id TEXT PRIMARY KEY,
  import_batch_id TEXT NOT NULL,
  vehicle_id TEXT NOT NULL,
  driver_id TEXT,
  operation_date DATE NOT NULL,
  distance_km NUMERIC(12,3) NOT NULL,
  passenger_count INTEGER NOT NULL DEFAULT 0,
  daily_revenue NUMERIC(14,2) NOT NULL DEFAULT 0,
  energy_consumed_kwh NUMERIC(12,3),
  packet_id TEXT REFERENCES trust_packets(packet_id),
  evidence_id TEXT REFERENCES digital_evidence(evidence_id),
  mrv_id TEXT,
  value_id TEXT,
  baseline_co2e_kg NUMERIC(14,6),
  ev_co2e_kg NUMERIC(14,6),
  reduction_co2e_kg NUMERIC(14,6),
  green_point INTEGER NOT NULL DEFAULT 0,
  validation_status TEXT NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS taxi_import_logs (
  import_log_id TEXT PRIMARY KEY,
  import_batch_id TEXT NOT NULL,
  row_number INTEGER NOT NULL,
  vehicle_id TEXT,
  status TEXT NOT NULL,
  reason TEXT,
  raw_row JSONB NOT NULL DEFAULT '{}'::jsonb,
  packet_id TEXT,
  evidence_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS green_point_ledger (
  ledger_id TEXT PRIMARY KEY,
  vehicle_id TEXT NOT NULL,
  driver_id TEXT,
  operation_date DATE NOT NULL,
  packet_id TEXT,
  evidence_id TEXT,
  mrv_id TEXT,
  point_amount INTEGER NOT NULL,
  reason TEXT NOT NULL DEFAULT 'CARBON_REDUCTION',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_taxi_daily_operations_vehicle_date
  ON taxi_daily_operations(vehicle_id, operation_date);

CREATE INDEX IF NOT EXISTS idx_taxi_daily_operations_packet_id
  ON taxi_daily_operations(packet_id);

CREATE INDEX IF NOT EXISTS idx_taxi_daily_operations_evidence_id
  ON taxi_daily_operations(evidence_id);

CREATE INDEX IF NOT EXISTS idx_taxi_import_logs_batch
  ON taxi_import_logs(import_batch_id);

CREATE INDEX IF NOT EXISTS idx_green_point_ledger_vehicle_date
  ON green_point_ledger(vehicle_id, operation_date);

-- Required audit events:
-- CSV_IMPORTED
-- PACKET_CREATED
-- HASH_GENERATED
-- SIGNATURE_CREATED
-- EVIDENCE_SEALED
-- TAXI_MRV_CALCULATED
-- POINT_ISSUED

