-- 005_incidents.sql: store major incidents (blocks, login failures, etc.)

CREATE TABLE IF NOT EXISTS scraper.incidents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT,
    incident_type   TEXT NOT NULL,  -- block_detected | login_failed | proxy_down | other
    severity        TEXT NOT NULL DEFAULT 'medium',
    message         TEXT,
    details         JSONB,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved        BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_incidents_source_time
    ON scraper.incidents (source, occurred_at);
