-- 002_scraper_runs.sql: track each scraper run

CREATE TABLE IF NOT EXISTS scraper.scraper_runs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT NOT NULL, -- Airflow run_id or custom UUID
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'running', -- running | success | failed | partial
    records_fetched INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraper_runs_source_started
    ON scraper.scraper_runs (source, started_at);
