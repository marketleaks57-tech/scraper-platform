-- 011_change_log.sql: track structural/platform changes

CREATE TABLE IF NOT EXISTS scraper.change_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor           TEXT NOT NULL DEFAULT 'system',  -- user / system
    scope           TEXT NOT NULL,                 -- scraper | schema | config
    target          TEXT NOT NULL,                 -- e.g., alfabeta.pipeline
    change_type     TEXT NOT NULL,                 -- deploy | rollback | hotfix
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_change_log_scope_target
    ON scraper.change_log (scope, target);
