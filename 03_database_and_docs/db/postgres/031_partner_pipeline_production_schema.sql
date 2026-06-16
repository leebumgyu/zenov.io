-- ZENOV Partner Pipeline Production Data Engine
-- LocalStorage is only a browser cache. Production partner pipeline data is stored here.

ALTER TABLE partners
  ADD COLUMN IF NOT EXISTS company_name TEXT,
  ADD COLUMN IF NOT EXISTS business_type TEXT,
  ADD COLUMN IF NOT EXISTS contact_name TEXT,
  ADD COLUMN IF NOT EXISTS contact_phone TEXT,
  ADD COLUMN IF NOT EXISTS contact_email TEXT,
  ADD COLUMN IF NOT EXISTS region TEXT,
  ADD COLUMN IF NOT EXISTS status TEXT,
  ADD COLUMN IF NOT EXISTS owner_id TEXT;

CREATE TABLE IF NOT EXISTS questionnaires (
  questionnaire_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  mobility_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  energy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  carbon_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  documents_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS partner_status_history (
  history_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  old_status TEXT,
  new_status TEXT NOT NULL,
  changed_by TEXT NOT NULL DEFAULT 'system',
  changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS partner_actions (
  action_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  action_title TEXT NOT NULL,
  action_status TEXT NOT NULL,
  owner_id TEXT,
  due_date DATE,
  memo TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meetings (
  meeting_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  meeting_date DATE,
  meeting_type TEXT,
  location TEXT,
  attendees_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  meeting_status TEXT NOT NULL DEFAULT 'REQUESTED',
  memo TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS proposals (
  proposal_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  proposal_type TEXT,
  proposal_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
  proposal_file_url TEXT,
  sent_date DATE,
  feedback TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sales_execution (
  execution_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  send_status TEXT NOT NULL DEFAULT 'DRAFT',
  view_status TEXT NOT NULL DEFAULT 'NOT_OPENED',
  feedback_type TEXT,
  conversion_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  followup_status TEXT NOT NULL DEFAULT 'TODO',
  execution_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sent_materials (
  send_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  material_type TEXT,
  material_title TEXT,
  recipient_name TEXT,
  recipient_email TEXT,
  sent_at TIMESTAMPTZ,
  sent_by TEXT,
  send_status TEXT NOT NULL DEFAULT 'DRAFT',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback_logs (
  feedback_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  feedback_type TEXT,
  feedback_content TEXT,
  received_at TIMESTAMPTZ,
  owner_id TEXT,
  next_action TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS partner_success (
  success_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  report_month TEXT NOT NULL,
  data_connected_days INTEGER NOT NULL DEFAULT 0,
  packets_collected INTEGER NOT NULL DEFAULT 0,
  valid_packets INTEGER NOT NULL DEFAULT 0,
  rejected_packets INTEGER NOT NULL DEFAULT 0,
  estimated_co2e NUMERIC(18,6) NOT NULL DEFAULT 0,
  estimated_carbon_value NUMERIC(18,2) NOT NULL DEFAULT 0,
  health_score NUMERIC(5,2) NOT NULL DEFAULT 0,
  health_status TEXT NOT NULL DEFAULT 'WATCH',
  expansion_value NUMERIC(18,2) NOT NULL DEFAULT 0,
  renewal_probability NUMERIC(5,2) NOT NULL DEFAULT 0,
  report_status TEXT NOT NULL DEFAULT 'NOT_CREATED',
  success_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(partner_id, report_month)
);

CREATE TABLE IF NOT EXISTS partner_uploaded_files (
  file_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  file_type TEXT NOT NULL,
  file_url TEXT NOT NULL,
  file_hash TEXT,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS partner_pipeline_audit_logs (
  log_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  event_type TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT,
  changed_by TEXT NOT NULL DEFAULT 'system',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partners_pipeline_status
  ON partners(status);

CREATE INDEX IF NOT EXISTS idx_questionnaires_partner
  ON questionnaires(partner_id, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_partner_actions_partner_status
  ON partner_actions(partner_id, action_status);

CREATE INDEX IF NOT EXISTS idx_meetings_partner_date
  ON meetings(partner_id, meeting_date DESC);

CREATE INDEX IF NOT EXISTS idx_partner_success_partner_month
  ON partner_success(partner_id, report_month DESC);

CREATE INDEX IF NOT EXISTS idx_partner_pipeline_audit_partner
  ON partner_pipeline_audit_logs(partner_id, created_at DESC);
