-- 013_scraper_session_events.sql: detailed session event log

CREATE TABLE IF NOT EXISTS scraper.scraper_session_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL,
    source          TEXT NOT NULL,
    account_id      TEXT NOT NULL,
    proxy_id        TEXT,
    event_type      TEXT NOT NULL,   -- cookies_saved | cookies_restored | login_success | login_failed | blocked
    details         JSONB,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraper_session_events_session
    ON scraper.scraper_session_events (session_id);
    