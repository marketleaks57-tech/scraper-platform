#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${1:-dev}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/config/env/${ENV_NAME}.yaml"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[setup_env] Missing env file: $ENV_FILE" >&2
  exit 1
fi

echo "[setup_env] Exporting environment variables from $ENV_FILE"
eval "$(
python - <<'PYCODE' "$ENV_FILE"
import os
import sys
import yaml

env_file = sys.argv[1]
with open(env_file, "r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle) or {}

for key, value in data.items():
    if isinstance(value, (str, int, float)):
        print(f"export {key.upper()}='{value}'")
PYCODE
)"

