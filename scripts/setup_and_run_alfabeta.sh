#!/bin/bash
# ============================================
#  Scraper Platform v5.0 - Linux Bootstrap
#  - Creates/uses .venv
#  - Installs requirements
#  - Sets env vars for AlfaBeta
#  - Runs AlfaBeta pipeline
# ============================================

set -e  # Exit on error

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[INFO] Working directory: $PWD"
echo ""

# --------------------------------------------
# 1) Ensure virtual environment exists
# --------------------------------------------
if [ ! -d ".venv" ]; then
    echo "[INFO] .venv not found. Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[INFO] Using existing .venv"
fi

# --------------------------------------------
# 2) Install / upgrade pip and requirements
# --------------------------------------------
echo ""
echo "[INFO] Upgrading pip inside venv..."
.venv/bin/pip install --upgrade pip

echo ""
echo "[INFO] Installing requirements.txt..."
.venv/bin/pip install -r requirements.txt

# --------------------------------------------
# 3) Set environment variables for this run
#    EDIT THESE for real credentials.
# --------------------------------------------
echo ""
echo "[INFO] Setting environment for AlfaBeta (session only)..."

# Fake browser so you can run without Chrome at first
export SCRAPER_PLATFORM_FAKE_BROWSER=1

# TODO: replace these with real site creds
export ALFABETA_USER_1=user
export ALFABETA_PASS_1=pass

# If you have proxies, uncomment and fill:
# export ALFABETA_PROXIES=ip1:port,ip2:port

# --------------------------------------------
# 4) Run AlfaBeta pipeline
# --------------------------------------------
echo ""
echo "[INFO] Running AlfaBeta pipeline..."
.venv/bin/python -m src.scrapers.alfabeta.pipeline

echo ""
echo "[INFO] Done. Check output/alfabeta/daily/ for CSV."
echo ""

