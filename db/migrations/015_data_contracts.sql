-- 015_data_contracts.sql: data contracts & SLAs per client/source

CREATE TABLE IF NOT EXISTS scraper.data_contracts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_name   TEXT NOT NULL,
    client_name     TEXT NOT NULL,
    source          TEXT NOT NULL,
    required_fields TEXT[] NOT NULL,
    freshness_hours INTEGER NOT NULL DEFAULT 24,
    min_daily_records INTEGER NOT NULL DEFAULT 0,
    sla_details     JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_contracts_source_client
    ON scraper.data_contracts (source, client_name);
