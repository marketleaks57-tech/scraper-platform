-- 012_scraper_sessions.sql: logical scraping sessions per source+account+proxy

CREATE TABLE IF NOT EXISTS scraper.scraper_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    account_id      TEXT NOT NULL,
    proxy_id        TEXT,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'active', -- active | expired | banned
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_scraper_sessions_source_account
    ON scraper.scraper_sessions (source, account_id);
