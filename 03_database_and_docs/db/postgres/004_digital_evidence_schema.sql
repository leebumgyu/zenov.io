-- ZENOV Digital Evidence Layer Schema V1
-- Root chain: packet_id -> evidence_id -> artifact_id -> integrity_report_id -> mrv_id -> value_id -> asset_id

CREATE TABLE IF NOT EXISTS digital_evidence (
  evidence_id TEXT PRIMARY KEY,
  packet_id TEXT NOT NULL REFERENCES trust_packets(packet_id),
  evidence_type TEXT NOT NULL,
  source_type TEXT NOT NULL,
  trust_score NUMERIC(5,2),
  evidence_hash TEXT NOT NULL,
  signature_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS evidence_artifacts (
  artifact_id TEXT PRIMARY KEY,
  evidence_id TEXT NOT NULL REFERENCES digital_evidence(evidence_id),
  artifact_type TEXT NOT NULL,
  file_path TEXT,
  file_hash TEXT NOT NULL,
  file_size BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integrity_reports (
  integrity_report_id TEXT PRIMARY KEY,
  evidence_id TEXT NOT NULL REFERENCES digital_evidence(evidence_id),
  hash_verified BOOLEAN NOT NULL DEFAULT FALSE,
  signature_verified BOOLEAN NOT NULL DEFAULT FALSE,
  canonical_verified BOOLEAN NOT NULL DEFAULT FALSE,
  verifier_name TEXT NOT NULL DEFAULT 'ZENOV_TRUST_LAYER',
  verification_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'PENDING'
);

CREATE TABLE IF NOT EXISTS calibration_records (
  calibration_id TEXT PRIMARY KEY,
  sensor_id TEXT NOT NULL,
  certificate_number TEXT,
  calibration_date DATE,
  expiration_date DATE,
  calibration_file TEXT,
  status TEXT NOT NULL DEFAULT 'UNKNOWN',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_sensor_mapping (
  mapping_id TEXT PRIMARY KEY,
  evidence_id TEXT NOT NULL REFERENCES digital_evidence(evidence_id),
  sensor_id TEXT,
  gateway_id TEXT,
  calibration_id TEXT REFERENCES calibration_records(calibration_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS evidence_id TEXT,
  ADD COLUMN IF NOT EXISTS asset_id TEXT;

ALTER TABLE mrv_results
  ADD COLUMN IF NOT EXISTS evidence_id TEXT;

CREATE INDEX IF NOT EXISTS idx_digital_evidence_packet_id
  ON digital_evidence(packet_id);

CREATE INDEX IF NOT EXISTS idx_digital_evidence_status
  ON digital_evidence(status);

CREATE INDEX IF NOT EXISTS idx_evidence_artifacts_evidence_id
  ON evidence_artifacts(evidence_id);

CREATE INDEX IF NOT EXISTS idx_integrity_reports_evidence_id
  ON integrity_reports(evidence_id);

CREATE INDEX IF NOT EXISTS idx_evidence_sensor_mapping_evidence_id
  ON evidence_sensor_mapping(evidence_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_evidence_id
  ON audit_logs(evidence_id);

CREATE INDEX IF NOT EXISTS idx_mrv_results_evidence_id
  ON mrv_results(evidence_id);

-- Required evidence events:
-- EVIDENCE_CREATED
-- EVIDENCE_VERIFIED
-- EVIDENCE_VERIFICATION_FAILED
-- INTEGRITY_REPORT_CREATED

