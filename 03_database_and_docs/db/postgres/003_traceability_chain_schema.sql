-- ZENOV Carbon Traceability Chain Schema V1

ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS mrv_id TEXT,
  ADD COLUMN IF NOT EXISTS value_id TEXT;

ALTER TABLE mrv_results
  ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'SUCCESS';

ALTER TABLE carbon_value_results
  ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'SUCCESS';

CREATE INDEX IF NOT EXISTS idx_audit_logs_mrv_id
  ON audit_logs (mrv_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_value_id
  ON audit_logs (value_id);

CREATE INDEX IF NOT EXISTS idx_mrv_results_status
  ON mrv_results (status);

CREATE INDEX IF NOT EXISTS idx_carbon_value_results_status
  ON carbon_value_results (status);

-- Required audit events:
-- MRV_CALCULATION_STARTED
-- MRV_CALCULATION_SUCCESS
-- MRV_CALCULATION_FAILED
-- CARBON_VALUE_STARTED
-- CARBON_VALUE_CALCULATED
-- CARBON_VALUE_FAILED
-- TRACEABILITY_CHAIN_COMPLETED
-- TRACEABILITY_CHAIN_BROKEN

-- Chain:
-- packet_id -> mrv_id -> value_id -> audit_logs
