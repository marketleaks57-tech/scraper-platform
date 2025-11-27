#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Running database migrations"
airflow db upgrade

echo "[entrypoint] Creating admin user if missing"
airflow users create \
    --username admin \
    --firstname Air \
    --lastname Flow \
    --role Admin \
    --email admin@example.com \
    --password "${AIRFLOW_ADMIN_PASSWORD:-admin}" || true

echo "[entrypoint] Starting scheduler"
airflow scheduler &

echo "[entrypoint] Starting webserver"
exec airflow webserver

