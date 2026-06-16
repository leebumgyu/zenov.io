-- ZENOV Operations Root Cause Drill-down Schema
-- Sprint 10 target: identify what failed and why within 30 seconds.

CREATE TABLE IF NOT EXISTS ops_retry_states (
  retry_id TEXT PRIMARY KEY,
  import_job_row_id TEXT NOT NULL,
  import_job_id TEXT,
  packet_id TEXT,
  reason_code TEXT NOT NULL,
  retry_status TEXT NOT NULL DEFAULT 'FAILED',
  retry_count INTEGER NOT NULL DEFAULT 0,
  last_retry_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dead_letter_queue (
  dlq_id TEXT PRIMARY KEY,
  import_job_row_id TEXT NOT NULL,
  import_job_id TEXT,
  vehicle_id TEXT,
  reason_code TEXT NOT NULL,
  raw_row JSONB NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'MANUAL_REVIEW_REQUIRED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ops_retry_states_job_row
  ON ops_retry_states(import_job_row_id);

CREATE INDEX IF NOT EXISTS idx_ops_retry_states_reason
  ON ops_retry_states(reason_code);

CREATE INDEX IF NOT EXISTS idx_dead_letter_reason
  ON dead_letter_queue(reason_code);
