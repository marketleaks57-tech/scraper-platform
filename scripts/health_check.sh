#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python}"

PYTHONPATH="$ROOT_DIR/src" \
  "$PYTHON" - <<'PYCODE'
from src.observability.healthchecks import run_health_checks

results = run_health_checks()
failed = [name for name, status in results.items() if not status["ok"]]
for name, status in results.items():
    marker = "OK" if status["ok"] else "FAIL"
    print(f"[health] {marker} {name}: {status['message']}")

if failed:
    raise SystemExit(f"Health checks failed: {failed}")
PYCODE

