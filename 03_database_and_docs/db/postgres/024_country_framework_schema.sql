-- ZENOV SPRINT 20 - ASEAN LOCALIZATION & MULTI-COUNTRY FRAMEWORK
-- Scope: config-driven country profiles, carbon factors, registry profiles, and report localization.

CREATE TABLE IF NOT EXISTS country_profiles (
    country_code TEXT PRIMARY KEY,
    country_name TEXT NOT NULL,
    language_code TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    timezone TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    profile_version TEXT NOT NULL DEFAULT '1.0.0',
    config_hash TEXT NOT NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS country_carbon_profiles (
    carbon_profile_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL REFERENCES country_profiles(country_code),
    grid_emission_factor NUMERIC(12,6) NOT NULL,
    grid_emission_unit TEXT NOT NULL,
    fuel_emission_factors JSONB NOT NULL DEFAULT '{}'::jsonb,
    mrv_methodologies JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_reference TEXT NOT NULL,
    effective_date DATE NOT NULL,
    source_version TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS country_registry_profiles (
    registry_profile_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL REFERENCES country_profiles(country_code),
    local_registry_name TEXT NOT NULL,
    government_reporting_format TEXT NOT NULL,
    registry_status TEXT NOT NULL DEFAULT 'CONFIGURED',
    submission_language TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS localized_report_templates (
    template_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL REFERENCES country_profiles(country_code),
    report_type TEXT NOT NULL,
    language_code TEXT NOT NULL,
    unit_system TEXT NOT NULL DEFAULT 'METRIC',
    template_version TEXT NOT NULL DEFAULT '1.0.0',
    required_sections JSONB NOT NULL DEFAULT '[]'::jsonb,
    labels JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS country_methodology_adapters (
    adapter_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL REFERENCES country_profiles(country_code),
    industry_type TEXT NOT NULL,
    base_methodology_id TEXT NOT NULL,
    local_methodology_id TEXT NOT NULL,
    local_methodology_version TEXT NOT NULL,
    adapter_status TEXT NOT NULL DEFAULT 'DRAFT',
    rules JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_country_methodology_adapters_country
    ON country_methodology_adapters(country_code);

CREATE INDEX IF NOT EXISTS idx_localized_report_templates_country
    ON localized_report_templates(country_code);
