-- 010_schema_signatures.sql: store DOM/schema signatures per source

CREATE TABLE IF NOT EXISTS scraper.schema_signatures (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,
    page_type       TEXT NOT NULL,      -- listing | product | login etc.
    signature_hash  TEXT NOT NULL,
    signature_json  JSONB NOT NULL,
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schema_signatures_source_page
    ON scraper.schema_signatures (source, page_type);
