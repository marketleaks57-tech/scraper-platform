-- 021_audit_events.sql: durable audit trail for compliance and incident investigation

CREATE TABLE IF NOT EXISTS scraper.audit_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type      TEXT NOT NULL,              -- generic, run, config_change, etc.
    source          TEXT,                       -- scraper source (if applicable)
    run_id          TEXT,                       -- scraper run_id (if applicable)
    payload         JSONB NOT NULL,            -- full event payload
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_created
    ON scraper.audit_events (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_events_event_type
    ON scraper.audit_events (event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_events_source_run
    ON scraper.audit_events (source, run_id) WHERE source IS NOT NULL AND run_id IS NOT NULL;

