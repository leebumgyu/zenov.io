-- ZENOV Partner Integration Hub Schema
-- Goal: onboard taxi companies, bus companies, CPOs, insurers, ERP, and IoT systems without code changes.

CREATE TABLE IF NOT EXISTS partners (
  partner_id TEXT PRIMARY KEY,
  partner_name TEXT NOT NULL,
  partner_type TEXT NOT NULL,
  source_system TEXT NOT NULL,
  data_format TEXT NOT NULL,
  lifecycle_status TEXT NOT NULL DEFAULT 'INVITED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (lifecycle_status IN (
    'INVITED',
    'ONBOARDING',
    'CONNECTED',
    'ACTIVE',
    'SUSPENDED'
  ))
);

CREATE TABLE IF NOT EXISTS partner_api_keys (
  api_key_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  label TEXT NOT NULL DEFAULT 'default',
  api_key_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_used_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS partner_data_mappings (
  mapping_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  source_type TEXT NOT NULL,
  standard_model TEXT NOT NULL,
  field_map JSONB NOT NULL,
  mapping_status TEXT NOT NULL DEFAULT 'MAPPING_OK',
  mapping_check JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS partner_integrations (
  integration_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  integration_type TEXT NOT NULL,
  endpoint_url TEXT,
  status TEXT NOT NULL DEFAULT 'CONNECTED',
  api_key_id TEXT REFERENCES partner_api_keys(api_key_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_health_check_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS partner_health_logs (
  health_log_id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(partner_id),
  source_type TEXT,
  event_type TEXT NOT NULL,
  event_status TEXT NOT NULL,
  message TEXT,
  mapping_errors JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partners_lifecycle
  ON partners(lifecycle_status);

CREATE INDEX IF NOT EXISTS idx_partner_mappings_partner_source
  ON partner_data_mappings(partner_id, source_type);

CREATE INDEX IF NOT EXISTS idx_partner_integrations_partner
  ON partner_integrations(partner_id, status);

CREATE INDEX IF NOT EXISTS idx_partner_health_partner
  ON partner_health_logs(partner_id, created_at DESC);

-- Lifecycle:
-- INVITED -> ONBOARDING -> CONNECTED -> ACTIVE -> SUSPENDED
--
-- Data Mapping:
-- T-money CSV -> taxi_daily_operation -> Evidence Layer
-- DTG -> vehicle_operation_log -> Evidence Layer
-- GPS -> mobility_tracking_log -> Evidence Layer
-- Charging API -> charging_session -> Evidence Layer
