#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python}"

SOURCE="${1:-alfabeta}"
RUN_ID="${2:-latest}"

echo "[replay] Replaying source=$SOURCE run=$RUN_ID"
PYTHONPATH="$ROOT_DIR/src" \
  "$PYTHON" -m src.tests_replay.replay_runner --source "$SOURCE" --run-id "$RUN_ID"

