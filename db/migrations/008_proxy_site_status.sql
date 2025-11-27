-- 008_proxy_site_status.sql: track proxy×site health

CREATE TABLE IF NOT EXISTS scraper.proxy_site_status (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    proxy_id        TEXT NOT NULL,
    last_success_at TIMESTAMPTZ,
    last_failure_at TIMESTAMPTZ,
    success_count   INTEGER NOT NULL DEFAULT 0,
    failure_count   INTEGER NOT NULL DEFAULT 0,
    last_error      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_proxy_site_status_source_proxy
    ON scraper.proxy_site_status (source, proxy_id);
