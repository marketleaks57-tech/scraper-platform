-- 014_data_versioning.sql: store dataset snapshots / versions

CREATE TABLE IF NOT EXISTS scraper.data_versioning (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT NOT NULL,
    snapshot_date   DATE NOT NULL,
    records_count   INTEGER NOT NULL DEFAULT 0,
    storage_path    TEXT NOT NULL,  -- e.g., s3://... or local path
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_versioning_source_date
    ON scraper.data_versioning (source, snapshot_date);
