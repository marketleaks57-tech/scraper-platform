-- 022_run_costs.sql: simplified per-run cost tracking

CREATE TABLE IF NOT EXISTS scraper.run_costs (
    source      text NOT NULL,
    run_id      text NOT NULL,
    cost_usd    numeric(18,6) NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (source, run_id)
);

CREATE INDEX IF NOT EXISTS idx_run_costs_source_updated
    ON scraper.run_costs (source, updated_at DESC);

