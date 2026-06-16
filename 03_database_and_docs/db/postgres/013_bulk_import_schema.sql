-- ZENOV 143-Vehicle Real Data Import Schema V1
-- Every row must be classified as SUCCESS, FAILED, DUPLICATE, or VERIFICATION_REJECTED.

CREATE TABLE IF NOT EXISTS import_jobs (
  import_job_id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  job_name TEXT,
  source_filename TEXT,
  total_rows INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  duplicate_count INTEGER NOT NULL DEFAULT 0,
  evidence_count INTEGER NOT NULL DEFAULT 0,
  mrv_count INTEGER NOT NULL DEFAULT 0,
  verification_pass_count INTEGER NOT NULL DEFAULT 0,
  asset_candidate_count INTEGER NOT NULL DEFAULT 0,
  success_rate NUMERIC(6,2) NOT NULL DEFAULT 0,
  report_id TEXT,
  summary_hash TEXT,
  status TEXT NOT NULL DEFAULT 'CREATED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS import_job_rows (
  import_job_row_id TEXT PRIMARY KEY,
  import_job_id TEXT NOT NULL REFERENCES import_jobs(import_job_id),
  row_number INTEGER NOT NULL,
  vehicle_id TEXT,
  operation_date DATE,
  driver_id TEXT,
  row_status TEXT NOT NULL,
  reason_code TEXT,
  packet_id TEXT,
  evidence_id TEXT,
  mrv_id TEXT,
  verification_id TEXT,
  asset_id TEXT,
  report_id TEXT,
  raw_row JSONB NOT NULL DEFAULT '{}'::jsonb,
  result_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS failed_import_rows (
  failed_row_id TEXT PRIMARY KEY,
  import_job_id TEXT NOT NULL REFERENCES import_jobs(import_job_id),
  row_number INTEGER NOT NULL,
  vehicle_id TEXT,
  reason_code TEXT NOT NULL,
  reason_message TEXT,
  raw_row JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_import_job_rows_job_id
  ON import_job_rows(import_job_id);

CREATE INDEX IF NOT EXISTS idx_import_job_rows_status
  ON import_job_rows(row_status);

CREATE INDEX IF NOT EXISTS idx_failed_import_rows_job_id
  ON failed_import_rows(import_job_id);
