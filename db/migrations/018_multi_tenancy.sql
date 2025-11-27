-- 018_multi_tenancy.sql: add tenant scoping for run and metric tables

-- Core run tracking
ALTER TABLE IF EXISTS scraper.scraper_runs
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_scraper_runs_tenant_started
    ON scraper.scraper_runs (tenant_id, started_at);

-- Run steps (for future compatibility)
ALTER TABLE IF EXISTS scraper.scraper_run_steps
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_scraper_run_steps_tenant_run
    ON scraper.scraper_run_steps (tenant_id, run_id);

-- Incidents
ALTER TABLE IF EXISTS scraper.incidents
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_incidents_tenant_time
    ON scraper.incidents (tenant_id, occurred_at);

-- Data quality metrics
ALTER TABLE IF EXISTS scraper.data_quality
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_data_quality_tenant_source_run
    ON scraper.data_quality (tenant_id, source, run_id);

-- Cost tracking metrics
ALTER TABLE IF EXISTS scraper.cost_tracking
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_cost_tracking_tenant_source_run
    ON scraper.cost_tracking (tenant_id, source, run_id);

-- Data versioning snapshots
ALTER TABLE IF EXISTS scraper.data_versioning
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_data_versioning_tenant_source_date
    ON scraper.data_versioning (tenant_id, source, snapshot_date);

-- Drift events associated with runs
ALTER TABLE IF EXISTS scraper.drift_events
    ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
CREATE INDEX IF NOT EXISTS idx_drift_events_tenant_detected
    ON scraper.drift_events (tenant_id, detected_at);
