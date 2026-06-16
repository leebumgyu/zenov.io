-- ZENOV MRV Verification Score Schema V1
-- Sprint 3 target: Packet -> Evidence -> MRV -> Verification Score -> Carbon Asset Candidate.

CREATE TABLE IF NOT EXISTS mrv_verification_records (
  verification_id TEXT PRIMARY KEY,
  packet_id TEXT REFERENCES trust_packets(packet_id),
  evidence_id TEXT REFERENCES digital_evidence(evidence_id),
  mrv_id TEXT,
  vehicle_id TEXT,
  operation_date DATE,
  verification_status TEXT NOT NULL DEFAULT 'PENDING',
  verification_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  completeness_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  integrity_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  source_reliability_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  methodology_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  anomaly_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  anomaly_flag BOOLEAN NOT NULL DEFAULT FALSE,
  anomaly_reason TEXT,
  methodology_id TEXT,
  methodology_version TEXT,
  reviewer TEXT NOT NULL DEFAULT 'ZENOV_VERIFICATION_ENGINE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mrv_verification_packet_id
  ON mrv_verification_records(packet_id);

CREATE INDEX IF NOT EXISTS idx_mrv_verification_evidence_id
  ON mrv_verification_records(evidence_id);

CREATE INDEX IF NOT EXISTS idx_mrv_verification_mrv_id
  ON mrv_verification_records(mrv_id);

CREATE INDEX IF NOT EXISTS idx_mrv_verification_status
  ON mrv_verification_records(verification_status);

-- Status model:
-- PENDING
-- UNDER_REVIEW
-- VERIFIED
-- CONDITIONALLY_VERIFIED
-- REJECTED

-- Score weights:
-- Completeness 30%
-- Integrity 30%
-- Source Reliability 20%
-- Methodology 10%
-- Anomaly 10%

