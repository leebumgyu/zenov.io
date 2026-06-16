-- ZENOV Language Review Workflow Schema
-- Goal: manage translation quality before exposing wording to production UI, reports, dashboards, certificates, and legal/settlement surfaces.

CREATE TABLE IF NOT EXISTS translation_keys (
  translation_key_id TEXT PRIMARY KEY,
  key_name TEXT NOT NULL,
  language_code TEXT NOT NULL,
  target_area TEXT NOT NULL,
  source_text TEXT NOT NULL,
  translated_text TEXT NOT NULL,
  fallback_text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'DRAFT',
  requires_legal_review BOOLEAN NOT NULL DEFAULT FALSE,
  legal_review_status TEXT NOT NULL DEFAULT 'NOT_REQUIRED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  UNIQUE (key_name, language_code),
  CHECK (status IN ('DRAFT', 'MACHINE_TRANSLATED', 'IN_REVIEW', 'APPROVED', 'REJECTED', 'PUBLISHED')),
  CHECK (target_area IN (
    'UI_MENU',
    'ERROR_MESSAGE',
    'MRV_REPORT',
    'CARBON_TRUST_CERTIFICATE',
    'PARTNER_DASHBOARD',
    'REFERRAL_DASHBOARD',
    'WALLET_POINT',
    'LEGAL_CERTIFICATION_SETTLEMENT'
  )),
  CHECK (legal_review_status IN ('NOT_REQUIRED', 'PENDING', 'APPROVED', 'REJECTED'))
);

CREATE TABLE IF NOT EXISTS language_reviewers (
  reviewer_id TEXT PRIMARY KEY,
  reviewer_name TEXT NOT NULL,
  reviewer_role TEXT NOT NULL,
  language_code TEXT NOT NULL,
  assigned_languages JSONB NOT NULL DEFAULT '[]'::jsonb,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (reviewer_role IN ('LANGUAGE_ADMIN', 'COUNTRY_REVIEWER', 'LEGAL_REVIEWER')),
  CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED'))
);

CREATE TABLE IF NOT EXISTS translation_reviews (
  review_id TEXT PRIMARY KEY,
  translation_key_id TEXT NOT NULL REFERENCES translation_keys(translation_key_id),
  reviewer_id TEXT NOT NULL REFERENCES language_reviewers(reviewer_id),
  reviewer_role TEXT NOT NULL,
  review_action TEXT NOT NULL,
  from_status TEXT NOT NULL,
  to_status TEXT NOT NULL,
  comment TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (review_action IN ('IN_REVIEW', 'APPROVED', 'REJECTED')),
  CHECK (reviewer_role IN ('LANGUAGE_ADMIN', 'COUNTRY_REVIEWER', 'LEGAL_REVIEWER'))
);

CREATE INDEX IF NOT EXISTS idx_translation_keys_language_status
  ON translation_keys(language_code, status);

CREATE INDEX IF NOT EXISTS idx_translation_keys_target_area
  ON translation_keys(target_area, requires_legal_review);

CREATE INDEX IF NOT EXISTS idx_translation_reviews_key
  ON translation_reviews(translation_key_id, created_at DESC);

-- Production exposure rules:
-- 1. Do not expose translations that are not APPROVED or PUBLISHED.
-- 2. Missing translations fallback to en-US.
-- 3. Legal/certification/settlement wording must be approved by LEGAL_REVIEWER before PUBLISHED.
-- 4. Do not use "Carbon Credit" before actual external certification. Use "Carbon Asset Candidate" or "Verified Carbon Data".
