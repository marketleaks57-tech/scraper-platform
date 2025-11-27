# Deployment Status

Use this document to summarize deployment readiness across environments. For deployment guides, see `docs/DEPLOYMENT.md`.

## Current snapshot
- Airflow DAGs validated in development.
- Optional dependencies (`psycopg2`, `selenium`) required for database-backed or browser-based runs.
- Docker Compose definitions available in `docker-compose*.yml` for local orchestration.

Update this file when promoting builds to staging or production.
