-- 003_drift_events.sql: DOM / schema drift events per source

CREATE TABLE IF NOT EXISTS scraper.drift_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity        TEXT NOT NULL DEFAULT 'medium', -- low | medium | high
    drift_type      TEXT NOT NULL,                 -- dom_structure | selector_missing | field_missing
    selector        TEXT,
    details         JSONB,
    resolved        BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_drift_events_source_detected
    ON scraper.drift_events (source, detected_at);
