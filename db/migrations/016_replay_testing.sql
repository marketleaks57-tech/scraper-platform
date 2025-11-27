-- 016_replay_testing.sql: store HTML snapshots and test results

CREATE TABLE IF NOT EXISTS scraper.replay_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    snapshot_type   TEXT NOT NULL,   -- listing | product | login
    storage_path    TEXT NOT NULL,   -- e.g., s3://..., or local path
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scraper.replay_test_results (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    snapshot_id     UUID NOT NULL,
    run_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success         BOOLEAN NOT NULL,
    warnings        JSONB,
    errors          JSONB
);

CREATE INDEX IF NOT EXISTS idx_replay_snapshots_source_type
    ON scraper.replay_snapshots (source, snapshot_type);
