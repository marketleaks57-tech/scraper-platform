# Technical Requirements

- Python environment with optional extras installed only when needed: `psycopg2` for database exporters and API routes that read from the DB; `selenium` for browser engines.
- Airflow configured to load DAGs under `dags/`, with access to configuration files in `config/`.
- Network egress aligned with proxy policies; HTTP engine is default while browser engines remain experimental.
- Database target configured for exporters; confirm credentials and schema availability before production runs.
- Frontend dashboard built with Node and Vite (`frontend-dashboard/`) for run monitoring.
