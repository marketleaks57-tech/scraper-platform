#!/usr/bin/env python3
"""
Apply raw SQL migrations in db/migrations in chronological order.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import psycopg2

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "db" / "migrations"


def iter_migrations() -> Iterable[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def apply_migrations() -> None:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER", "scraper"),
        password=os.getenv("DB_PASSWORD", "scraper"),
        dbname=os.getenv("DB_NAME", "scraper"),
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for migration in iter_migrations():
                print(f"[migrate] Applying {migration.name}")
                sql = migration.read_text(encoding="utf-8")
                cur.execute(sql)
    finally:
        conn.close()


def main() -> int:
    apply_migrations()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

