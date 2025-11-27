"""
Database cleanup / archival utility.

Removes old runs, run steps, and incident records according to retention
settings in ``config/settings.yaml``. Optional S3 archival is supported
when ``boto3`` is installed and a bucket is provided.

Usage examples:
    python -m tools.cleanup_db --dry-run
    python -m tools.cleanup_db --archive-s3-bucket my-bucket --s3-prefix backups/run-history
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    psycopg2 = None  # type: ignore
    sql = None  # type: ignore
    RealDictCursor = None  # type: ignore
    POSTGRES_AVAILABLE = False

try:  # Optional dependency
    import boto3
except ImportError:  # pragma: no cover - optional dependency
    boto3 = None  # type: ignore

from src.common.config_loader import load_config
from src.common.logging_utils import get_logger
from src.scheduler import scheduler_db_adapter

log = get_logger("cleanup-db")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_rows(rows: Iterable[Dict[str, Any]]) -> str:
    def _convert(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    return "\n".join(json.dumps({k: _convert(v) for k, v in row.items()}) for row in rows)


def _archive_to_s3(
    *, bucket: str, prefix: str, label: str, rows: List[Dict[str, Any]]
) -> Optional[str]:
    if not rows:
        return None
    if boto3 is None:
        log.warning(
            "Cannot archive %s rows to s3://%s/%s — boto3 not installed", label, bucket, prefix
        )
        return None

    key = f"{prefix.rstrip('/')}/{label}-{_utc_now().strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    body = _serialize_rows(rows)

    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))
    log.info("Archived %s rows to s3://%s/%s", label, bucket, key)
    return key


def _load_retention(config: dict | None = None, config_path: Path | None = None) -> dict:
    if config is not None:
        cfg = config
    elif config_path:
        cfg = load_config(config_dir=config_path)
    else:
        cfg = load_config()
    retention = cfg.get("retention", {}) or {}
    return {
        "runs_days": int(retention.get("runs_days", 90)),
        "incidents_days": int(retention.get("incidents_days", 180)),
    }


def _table_exists(cur, schema: str, table: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        LIMIT 1
        """,
        (schema, table),
    )
    return cur.fetchone() is not None


def _column_exists(cur, schema: str, table: str, column: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s AND column_name = %s
        LIMIT 1
        """,
        (schema, table, column),
    )
    return cur.fetchone() is not None


def cleanup_postgres(
    *,
    conn,
    runs_days: int,
    incidents_days: int,
    dry_run: bool,
    archive_bucket: Optional[str],
    archive_prefix: str,
) -> None:
    if not POSTGRES_AVAILABLE:
        log.warning("psycopg2 is not available; skipping Postgres cleanup")
        return

    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        run_cutoff = _utc_now() - timedelta(days=runs_days)
        incident_cutoff = _utc_now() - timedelta(days=incidents_days)

        if _table_exists(cur, "scraper", "scraper_runs"):
            cur.execute(
                sql.SQL("SELECT * FROM {} WHERE {} < %s").format(
                    sql.Identifier("scraper", "scraper_runs"), sql.Identifier("started_at")
                ),
                (run_cutoff,),
            )
            old_runs = cur.fetchall()
            log.info("Found %d scraper_runs rows older than %s", len(old_runs), run_cutoff.date())

            if archive_bucket:
                _archive_to_s3(
                    bucket=archive_bucket,
                    prefix=archive_prefix,
                    label="scraper_runs",
                    rows=[dict(r) for r in old_runs],
                )

            if not dry_run and old_runs:
                cur.execute(
                    sql.SQL("DELETE FROM {} WHERE {} < %s").format(
                        sql.Identifier("scraper", "scraper_runs"), sql.Identifier("started_at")
                    ),
                    (run_cutoff,),
                )
                log.info("Deleted %d scraper_runs rows", cur.rowcount)

        if _table_exists(cur, "scraper", "run_steps") and _column_exists(
            cur, "scraper", "run_steps", "started_at"
        ):
            cur.execute(
                sql.SQL("SELECT * FROM {} WHERE {} < %s").format(
                    sql.Identifier("scraper", "run_steps"), sql.Identifier("started_at")
                ),
                (run_cutoff,),
            )
            old_steps = cur.fetchall()
            log.info("Found %d run_steps rows older than %s", len(old_steps), run_cutoff.date())

            if archive_bucket:
                _archive_to_s3(
                    bucket=archive_bucket,
                    prefix=archive_prefix,
                    label="run_steps",
                    rows=[dict(row) for row in old_steps],
                )

            if not dry_run and old_steps:
                cur.execute(
                    sql.SQL("DELETE FROM {} WHERE {} < %s").format(
                        sql.Identifier("scraper", "run_steps"), sql.Identifier("started_at")
                    ),
                    (run_cutoff,),
                )
                log.info("Deleted %d run_steps rows", cur.rowcount)

        if _table_exists(cur, "scraper", "incidents"):
            cur.execute(
                sql.SQL("SELECT * FROM {} WHERE {} < %s").format(
                    sql.Identifier("scraper", "incidents"), sql.Identifier("occurred_at")
                ),
                (incident_cutoff,),
            )
            old_incidents = cur.fetchall()
            log.info(
                "Found %d incidents older than %s", len(old_incidents), incident_cutoff.date()
            )

            if archive_bucket:
                _archive_to_s3(
                    bucket=archive_bucket,
                    prefix=archive_prefix,
                    label="incidents",
                    rows=[dict(row) for row in old_incidents],
                )

            if not dry_run and old_incidents:
                cur.execute(
                    sql.SQL("DELETE FROM {} WHERE {} < %s").format(
                        sql.Identifier("scraper", "incidents"), sql.Identifier("occurred_at")
                    ),
                    (incident_cutoff,),
                )
                log.info("Deleted %d incident rows", cur.rowcount)

        conn.commit()
    finally:
        cur.close()


def cleanup_sqlite_runs(
    *,
    db_path: Path,
    runs_days: int,
    dry_run: bool,
    archive_bucket: Optional[str],
    archive_prefix: str,
) -> None:
    if not db_path.exists():
        log.info("Run tracking DB not found at %s; skipping SQLite cleanup", db_path)
        return

    cutoff = _utc_now() - timedelta(days=runs_days)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        runs = conn.execute("SELECT * FROM runs").fetchall()
        old_runs = [r for r in runs if datetime.fromisoformat(r["started_at"]) < cutoff]
        run_ids = [r["run_id"] for r in old_runs]

        log.info("Found %d SQLite runs older than %s", len(old_runs), cutoff.date())

        old_steps: list[sqlite3.Row] = []
        if run_ids:
            placeholders = ",".join("?" for _ in run_ids)
            step_query = f"SELECT * FROM run_steps WHERE run_id IN ({placeholders})"
            old_steps = conn.execute(step_query, run_ids).fetchall()

        if archive_bucket:
            _archive_to_s3(
                bucket=archive_bucket,
                prefix=archive_prefix,
                label="run_tracking_runs",
                rows=[dict(row) for row in old_runs],
            )
            if old_steps:
                _archive_to_s3(
                    bucket=archive_bucket,
                    prefix=archive_prefix,
                    label="run_tracking_steps",
                    rows=[dict(row) for row in old_steps],
                )

        if not dry_run and run_ids:
            placeholders = ",".join("?" for _ in run_ids)
            conn.execute(f"DELETE FROM run_steps WHERE run_id IN ({placeholders})", run_ids)
            conn.execute(f"DELETE FROM runs WHERE run_id IN ({placeholders})", run_ids)
            conn.commit()
            log.info(
                "Deleted %d SQLite run rows and %d step rows", len(run_ids), len(old_steps)
            )
    finally:
        conn.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cleanup old run and incident records")
    parser.add_argument("--runs-days", type=int, help="Override run retention in days")
    parser.add_argument(
        "--incidents-days", type=int, help="Override incident retention in days"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print matches without deleting")
    parser.add_argument(
        "--archive-s3-bucket", type=str, help="S3 bucket to upload JSONL archives before delete"
    )
    parser.add_argument(
        "--s3-prefix", type=str, default="db-archive", help="Prefix/key path for S3 archives"
    )
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        help="Optional override for run tracking SQLite database path",
    )
    parser.add_argument(
        "--skip-postgres", action="store_true", help="Skip Postgres cleanup even if reachable"
    )
    parser.add_argument(
        "--skip-sqlite", action="store_true", help="Skip run tracking SQLite cleanup"
    )
    return parser


def _connect_postgres(config: dict):
    if not POSTGRES_AVAILABLE:
        raise ImportError("psycopg2 is required for Postgres cleanup")

    db_url = os.getenv("DB_URL")
    if db_url:
        return psycopg2.connect(db_url)

    db_cfg = config.get("database", {})
    return psycopg2.connect(
        host=os.getenv("DB_HOST", db_cfg.get("host", "localhost")),
        port=os.getenv("DB_PORT", str(db_cfg.get("port", "5432"))),
        user=os.getenv("DB_USER", db_cfg.get("user", "scraper_user")),
        password=os.getenv("DB_PASS", db_cfg.get("password", "scraper_password")),
        dbname=os.getenv("DB_NAME", db_cfg.get("name", "scraper_db")),
    )


def main() -> None:
    args = build_arg_parser().parse_args()
    config = load_config()
    retention = _load_retention(config=config)

    runs_days = args.runs_days or retention["runs_days"]
    incidents_days = args.incidents_days or retention["incidents_days"]

    if not args.skip_postgres:
        if not POSTGRES_AVAILABLE:
            log.warning("psycopg2 not installed; skipping Postgres cleanup")
        else:
            try:
                with _connect_postgres(config) as pg_conn:
                    cleanup_postgres(
                        conn=pg_conn,
                        runs_days=runs_days,
                        incidents_days=incidents_days,
                        dry_run=args.dry_run,
                        archive_bucket=args.archive_s3_bucket,
                        archive_prefix=args.s3_prefix,
                    )
            except Exception as exc:  # pragma: no cover - runtime connectivity
                log.warning("Postgres cleanup skipped due to connection error: %s", exc)

    if not args.skip_sqlite:
        sqlite_path = args.sqlite_path or scheduler_db_adapter._db_path()
        cleanup_sqlite_runs(
            db_path=sqlite_path,
            runs_days=runs_days,
            dry_run=args.dry_run,
            archive_bucket=args.archive_s3_bucket,
            archive_prefix=args.s3_prefix,
        )


if __name__ == "__main__":
    main()
