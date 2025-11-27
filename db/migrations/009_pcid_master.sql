-- 009_pcid_master.sql: product code mapping table

CREATE TABLE IF NOT EXISTS scraper.pcid_master (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pcid            TEXT NOT NULL,          -- internal product code
    source          TEXT NOT NULL,
    source_product_id TEXT NOT NULL,
    name            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_pcid_master_source_sourcepid
    ON scraper.pcid_master (source, source_product_id);
