# DB Export Flow

Database exports capture run outputs for downstream consumption.

## Targets
- Postgres/Neon stores raw scraper outputs, normalized product records, PCID mappings, run metadata, and audit logs.
- Legacy exports are documented in prior runbooks; keep compatibility notes when maintaining older clients.

## Steps
1. Pipeline exporter writes raw results and normalized data with run identifiers.
2. Audit and metadata records track start/end times, status, and errors.
3. Downstream analytics or dashboards read from the export tables.

## Notes
- Configure database credentials before enabling DB exporters.
- Optional dependency: install `psycopg2` (or `psycopg2-binary`) only when DB exporters are active.
