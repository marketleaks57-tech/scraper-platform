"""
dump_cost_runs_stub.py
------------------------------------
Dump cost tracking information from:
  1) Postgres (if available)
  2) Fallback: local JSONL log (cost_runs.jsonl)

Usage:
    python -m tools.dump_cost_runs_stub
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from src.common.paths import LOGS_DIR


LOCAL_COST_LOG = LOGS_DIR / "cost_runs.jsonl"


def pg_fetch_cost_runs():
    """Try to fetch cost runs from Postgres."""
    if not POSTGRES_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "scraper_user"),
            password=os.getenv("DB_PASS", "scraper_password"),
            dbname=os.getenv("DB_NAME", "scraper_db"),
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT source, run_id, proxy_cost_usd, compute_cost_usd, other_cost_usd, currency, created_at
            FROM scraper.cost_tracking
            ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("[WARN] Cannot fetch Postgres cost data:", e)
        return None


def local_fetch_cost_runs():
    """Parse local cost_runs.jsonl."""
    if not LOCAL_COST_LOG.exists():
        print("No local cost log found at:", LOCAL_COST_LOG)
        return []

    rows = []
    for line in LOCAL_COST_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def dump_costs():
    """Dump cost tracking information from Postgres or local JSONL log."""
    print("\n=== Cost Tracking Dump ===\n")

    if POSTGRES_AVAILABLE:
        rows = pg_fetch_cost_runs()
        if rows:
            print("[INFO] Loaded cost data from Postgres.\n")
            for (source, run_id, proxy_cost, compute_cost, other_cost, currency, ts) in rows:
                print(f"- Source: {source}")
                print(f"  Run: {run_id}")
                print(f"  Proxy Cost:   {proxy_cost} {currency}")
                print(f"  Compute Cost: {compute_cost} {currency}")
                print(f"  Other Cost:   {other_cost} {currency}")
                print(f"  Timestamp:    {ts}")
                print("")
            return

    # Fallback to local JSONL
    print("[INFO] Postgres not available — using local JSON log.\n")
    rows = local_fetch_cost_runs()

    if not rows:
        print("(no local cost entries found)")
        return

    total = 0
    for r in rows:
        total_run = r.get("proxy_cost_usd", 0) + r.get("compute_cost_usd", 0) + r.get("other_cost_usd", 0)
        total += total_run

        print(f"- Source: {r.get('source')} | Run: {r.get('run_id')}")
        print(f"  Proxy Cost:   {r.get('proxy_cost_usd')}")
        print(f"  Compute Cost: {r.get('compute_cost_usd')}")
        print(f"  Other Cost:   {r.get('other_cost_usd')}")
        print(f"  Total:        {total_run:.4f} USD")
        print(f"  Timestamp:    {r.get('created_at')}")
        print("")

    print("=== Summary ===")
    print(f"Total aggregated cost: {total:.4f} USD\n")


def main():
    dump_costs()


if __name__ == "__main__":
    main()
