-- ZENOV Trust Layer PostgreSQL Schema V1
-- Purpose: Store Trust Packet metadata, audit trail, reject logs, and Global ID registry.

CREATE TABLE IF NOT EXISTS global_ids (
  zenov_id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  region TEXT NOT NULL,
  domain TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS trust_packets (
  packet_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  site_id TEXT NOT NULL,
  asset_id TEXT,
  sensor_id TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  sequence_no BIGINT NOT NULL,
  payload_hash TEXT NOT NULL,
  signature TEXT NOT NULL,
  validation_status TEXT NOT NULL CHECK (validation_status IN ('PENDING', 'VALIDATED', 'REJECTED')),
  raw_packet JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trust_packets_source_sequence
  ON trust_packets (source_id, sequence_no);

CREATE INDEX IF NOT EXISTS idx_trust_packets_site_timestamp
  ON trust_packets (site_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_trust_packets_asset_sensor
  ON trust_packets (asset_id, sensor_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_trust_packets_payload_hash_unique
  ON trust_packets (payload_hash);

CREATE TABLE IF NOT EXISTS audit_logs (
  audit_id BIGSERIAL PRIMARY KEY,
  packet_id TEXT NOT NULL REFERENCES trust_packets(packet_id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_status TEXT NOT NULL DEFAULT 'INFO',
  mrv_id TEXT,
  value_id TEXT,
  message TEXT,
  actor TEXT NOT NULL DEFAULT 'system',
  detail JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_packet_id
  ON audit_logs (packet_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type
  ON audit_logs (event_type);

CREATE TABLE IF NOT EXISTS reject_logs (
  reject_id BIGSERIAL PRIMARY KEY,
  packet_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  reason_message TEXT,
  raw_packet JSONB NOT NULL,
  validator_version TEXT NOT NULL,
  rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reject_logs_packet_id
  ON reject_logs (packet_id);

CREATE INDEX IF NOT EXISTS idx_reject_logs_reason_code
  ON reject_logs (reason_code);

CREATE INDEX IF NOT EXISTS idx_reject_logs_rejected_at
  ON reject_logs (rejected_at);

-- Storage rules:
-- 1. Failed validation data is never deleted; it is preserved in reject_logs.
-- 2. Only validated data should be written to InfluxDB sensor_readings.
-- 3. PostgreSQL stores Trust metadata; InfluxDB stores sensor time-series values.
-- 4. packet_id must connect trust_packets, audit_logs, reject_logs, and sensor_readings.
