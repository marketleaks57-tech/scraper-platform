-- 017_add_fk_indexes.sql
-- Add indexes on common foreign keys for stability and performance.

BEGIN;

-- Drift events per run
CREATE INDEX IF NOT EXISTS idx_drift_events_run_id
    ON scraper.drift_events (run_id);

-- Incidents per run
CREATE INDEX IF NOT EXISTS idx_incidents_run_id
    ON scraper.incidents (run_id);

-- Data quality metrics per run
CREATE INDEX IF NOT EXISTS idx_data_quality_run_id
    ON scraper.data_quality (run_id);

-- Cost tracking per run
CREATE INDEX IF NOT EXISTS idx_cost_tracking_run_id
    ON scraper.cost_tracking (run_id);

-- Dataset snapshots per run
CREATE INDEX IF NOT EXISTS idx_data_versioning_run_id
    ON scraper.data_versioning (run_id);

COMMIT;
