-- 020_product_records.sql: store actual scraper output records

CREATE TABLE IF NOT EXISTS scraper.product_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    run_id          TEXT NOT NULL,
    product_url     TEXT,
    name            TEXT,
    price           NUMERIC(12, 2),
    currency        TEXT,
    company         TEXT,
    pcid            TEXT,
    pcid_confidence NUMERIC(5, 4),
    version         TEXT,
    record_data     JSONB NOT NULL,  -- Full record as JSON for flexibility
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id        TEXT NOT NULL DEFAULT 'default'
);

CREATE INDEX IF NOT EXISTS idx_product_records_source_run
    ON scraper.product_records (source, run_id);

CREATE INDEX IF NOT EXISTS idx_product_records_created
    ON scraper.product_records (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_product_records_pcid
    ON scraper.product_records (pcid) WHERE pcid IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_product_records_tenant_source
    ON scraper.product_records (tenant_id, source, created_at);

