# file: tools/backfill_run.py
"""
CLI to trigger a backfill (re-run) for a given source and date/range.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill scraper runs for a source.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--start-date", required=False, help="Optional start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=False, help="Optional end date (YYYY-MM-DD).")
    args = parser.parse_args()

    # Wire this into Airflow / your orchestrator as needed.
    print(
        {
            "status": "scheduled",
            "source": args.source,
            "start_date": args.start_date,
            "end_date": args.end_date,
        }
    )


if __name__ == "__main__":
    main()
