-- ZENOV Sprint 22 - Executive AI Copilot & Audit Intelligence
-- AI is read-only. It explains verified data and never creates assets, approves
-- verification, registers registry records, or changes methodology.

CREATE TABLE IF NOT EXISTS copilot_query_logs (
    query_id TEXT PRIMARY KEY,
    actor_role TEXT NOT NULL,
    question TEXT NOT NULL,
    intent TEXT NOT NULL,
    response_text TEXT NOT NULL,
    source_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    forbidden_action_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_intelligence_explanations (
    explanation_id TEXT PRIMARY KEY,
    lookup_type TEXT NOT NULL,
    lookup_id TEXT NOT NULL,
    packet_id TEXT,
    evidence_id TEXT,
    mrv_id TEXT,
    verification_id TEXT,
    asset_id TEXT,
    registry_id TEXT,
    explanation_text TEXT NOT NULL,
    genealogy JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_explanations (
    explanation_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    packet_id TEXT,
    data_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    methodology_id TEXT,
    methodology_version TEXT,
    verification_process JSONB NOT NULL DEFAULT '{}'::jsonb,
    explanation_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_copilot_query_logs_created_at
    ON copilot_query_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_intelligence_lookup
    ON audit_intelligence_explanations (lookup_type, lookup_id);

CREATE INDEX IF NOT EXISTS idx_evidence_explanations_evidence
    ON evidence_explanations (evidence_id);
