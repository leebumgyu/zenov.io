-- ZENOV Carbon Asset Candidate Schema V1
-- Carbon Asset Candidate is not a Carbon Credit.
-- It is a verified MRV data package that may later become a carbon asset or credit
-- after external verification, certification, and registry review.

CREATE TABLE IF NOT EXISTS carbon_asset_candidates (
  candidate_id TEXT PRIMARY KEY,
  serial_number TEXT NOT NULL UNIQUE,
  packet_id TEXT REFERENCES trust_packets(packet_id),
  evidence_id TEXT REFERENCES digital_evidence(evidence_id),
  mrv_id TEXT,
  verification_id TEXT REFERENCES mrv_verification_records(verification_id),
  source_type TEXT NOT NULL,
  vehicle_id TEXT,
  owner_entity TEXT NOT NULL,
  vintage_year INTEGER NOT NULL,
  credit_unit TEXT NOT NULL DEFAULT 'tCO2e',
  issued_quantity_tco2e NUMERIC(18,6) NOT NULL DEFAULT 0,
  retired_quantity_tco2e NUMERIC(18,6) NOT NULL DEFAULT 0,
  estimated_value_krw NUMERIC(18,2) NOT NULL DEFAULT 0,
  estimated_value_usd NUMERIC(18,2) NOT NULL DEFAULT 0,
  verification_score NUMERIC(5,2) NOT NULL,
  candidate_status TEXT NOT NULL DEFAULT 'CANDIDATE',
  registry_status TEXT NOT NULL DEFAULT 'NOT_REGISTERED',
  registry_id TEXT,
  legal_disclaimer TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_carbon_asset_candidates_packet_id
  ON carbon_asset_candidates(packet_id);

CREATE INDEX IF NOT EXISTS idx_carbon_asset_candidates_evidence_id
  ON carbon_asset_candidates(evidence_id);

CREATE INDEX IF NOT EXISTS idx_carbon_asset_candidates_mrv_id
  ON carbon_asset_candidates(mrv_id);

CREATE INDEX IF NOT EXISTS idx_carbon_asset_candidates_status
  ON carbon_asset_candidates(candidate_status, registry_status);

-- Candidate state model:
-- CANDIDATE
-- UNDER_REVIEW
-- ELIGIBLE_FOR_REGISTRY
-- SUBMITTED_TO_REGISTRY
-- REGISTERED
-- RETIRED

-- Registry state model:
-- NOT_REGISTERED
-- SUBMITTED
-- REGISTERED
-- RETIRED

