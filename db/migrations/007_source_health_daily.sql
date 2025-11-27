-- 007_source_health_daily.sql: daily source health aggregates

CREATE TABLE IF NOT EXISTS scraper.source_health_daily (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source              TEXT NOT NULL,
    date                DATE NOT NULL,
    total_runs          INTEGER NOT NULL DEFAULT 0,
    successful_runs     INTEGER NOT NULL DEFAULT 0,
    failed_runs         INTEGER NOT NULL DEFAULT 0,
    avg_records         INTEGER NOT NULL DEFAULT 0,
    avg_latency_seconds NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_source_health_daily_source_date
    ON scraper.source_health_daily (source, date);
