#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[migrate] Applying database migrations"
PYTHONPATH="$ROOT_DIR/src" \
  alembic upgrade head || \
  python "$ROOT_DIR/scripts/run_sql_migrations.py"

