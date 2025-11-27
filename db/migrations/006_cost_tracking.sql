-- 006_cost_tracking.sql: per-run cost breakdown

CREATE TABLE IF NOT EXISTS scraper.cost_tracking (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT NOT NULL,
    proxy_cost_usd  NUMERIC(12,4) NOT NULL DEFAULT 0,
    compute_cost_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
    other_cost_usd  NUMERIC(12,4) NOT NULL DEFAULT 0,
    currency        TEXT NOT NULL DEFAULT 'USD',
    tenant_id       TEXT NOT NULL DEFAULT 'default',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_source_run
    ON scraper.cost_tracking (source, run_id);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_tenant_source
    ON scraper.cost_tracking (tenant_id, source, created_at DESC);
