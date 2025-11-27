-- 004_data_quality.sql: store QC stats per run

CREATE TABLE IF NOT EXISTS scraper.data_quality (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source              TEXT NOT NULL,
    run_id              TEXT NOT NULL,
    total_records       INTEGER NOT NULL DEFAULT 0,
    passed_records      INTEGER NOT NULL DEFAULT 0,
    failed_records      INTEGER NOT NULL DEFAULT 0,
    failure_reasons     JSONB, -- map of reason -> count
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_quality_source_run
    ON scraper.data_quality (source, run_id);
