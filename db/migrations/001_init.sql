-- 001_init.sql: base extension and schema

CREATE SCHEMA IF NOT EXISTS scraper;

-- Optional: for UUIDs / timestamps
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
