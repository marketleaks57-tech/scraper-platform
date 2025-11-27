-- 019_schema_version.sql: track applied schema version

CREATE TABLE IF NOT EXISTS scraper.schema_version (
    id          INTEGER PRIMARY KEY,
    version     INTEGER NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_schema_version_singleton
    ON scraper.schema_version (id);

CREATE INDEX IF NOT EXISTS idx_schema_version_updated_at
    ON scraper.schema_version (updated_at);
