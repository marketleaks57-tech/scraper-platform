"""
run_repair_session.py
--------------------------------------
Repair/clean session cookie files for a specific source
(or all sources).

Usage:
    python -m tools.run_repair_session --source alfabeta
    python -m tools.run_repair_session --all
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from src.agents.deepagent_repair_engine import run_repair_session as agent_run_repair_session
from src.agents.repair_loop import run_repair_loop
from src.common.paths import COOKIES_DIR, SESSION_LOGS_DIR


def log_event(source: str, session_file: Path, event_type: str, msg: str) -> None:
    """Append a repair event to session_events.jsonl."""
    SESSION_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SESSION_LOGS_DIR / "session_events.jsonl"
    ev = {
        "ts": datetime.utcnow().isoformat(),
        "event_type": f"repair::{event_type}",
        "source": source,
        "session_file": str(session_file),
        "msg": msg,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev) + "\n")


def is_expired(cookie_file_path: Path, hours: int = 12) -> bool:
    """Check if cookie file is expired based on file modification time."""
    try:
        mtime = datetime.fromtimestamp(cookie_file_path.stat().st_mtime)
        return (datetime.utcnow() - mtime) > timedelta(hours=hours)
    except Exception:
        return True


def repair_for_source(source: str) -> None:
    """Repair session cookies for a specific source."""
    print(f"\n=== Repairing sessions for source: {source} ===")

    found = False

    for cookie_file in COOKIES_DIR.glob(f"{source}__*.json"):
        found = True
        try:
            raw = cookie_file.read_text(encoding="utf-8")
            js = json.loads(raw)
        except Exception as e:
            print(f"[CORRUPT] {cookie_file} — deleting. Error: {e}")
            cookie_file.unlink(missing_ok=True)
            log_event(source, cookie_file, "delete_corrupt", f"invalid JSON: {e}")
            continue

        # Cookie files are stored as JSON arrays (list of cookie dicts)
        # Check if it's a valid array
        if not isinstance(js, list):
            print(f"[INVALID] {cookie_file} — not a JSON array, deleting.")
            cookie_file.unlink(missing_ok=True)
            log_event(source, cookie_file, "delete_invalid_format", "not a JSON array")
            continue

        # Check expiration based on file mtime
        if is_expired(cookie_file, hours=12):
            print(f"[EXPIRED] {cookie_file} — deleting (older than 12 hours).")
            cookie_file.unlink(missing_ok=True)
            log_event(source, cookie_file, "delete_expired", "cookie TTL exceeded")
            continue

        # Basic sanity check - ensure it's a list of cookie-like objects
        if len(js) > 0 and not isinstance(js[0], dict):
            print(f"[INVALID] {cookie_file} — invalid cookie format, deleting.")
            cookie_file.unlink(missing_ok=True)
            log_event(source, cookie_file, "delete_invalid_format", "invalid cookie objects")
            continue

        print(f"[OK] {cookie_file} valid ({len(js)} cookies).")

    if not found:
        print("No cookie files found for this source.")


def repair_all() -> None:
    """Repair sessions across all sources."""
    print("\n=== Running full session repair ===")
    seen_sources = set()

    for cookie_file in COOKIES_DIR.glob("*.json"):
        parts = cookie_file.name.split("__", 1)
        if len(parts) == 2:
            seen_sources.add(parts[0])

    if not seen_sources:
        print("No session files found anywhere.")
        return

    for src in seen_sources:
        repair_for_source(src)


def run_agent_repair(source: str, selectors: Path | None = None) -> None:
    """Invoke the DeepAgent repair engine and log results without crashing."""

    print(f"\n=== Running agent repair session for {source} ===")
    try:
        results = agent_run_repair_session(source, selectors_path=selectors)
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Agent repair failed: {exc}")
        return

    if not results:
        print("No patches proposed (no diffs detected or snapshots missing).")
        return

    for res in results:
        print(f"Patch for {res.field}: applied={res.applied}, reason={res.reason}")


def main() -> None:
    """Main entry point for session repair tool."""
    parser = argparse.ArgumentParser(description="Repair broken session cookies.")
    parser.add_argument("--source", help="Repair only one source")
    parser.add_argument("--all", action="store_true", help="Repair all sources")
    parser.add_argument(
        "--patch",
        action="store_true",
        help="Invoke the agentic repair stub for the provided --source",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run the full repair loop (anomaly detection + patch proposal)",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run_id to focus repair loop on specific run",
    )
    parser.add_argument(
        "--max-patches",
        type=int,
        default=10,
        help="Maximum number of patches to propose (default: 10)",
    )
    parser.add_argument(
        "--selectors",
        type=Path,
        help="Optional custom selectors.json path for the patch workflow",
    )

    args = parser.parse_args()

    if args.loop:
        if not args.source:
            print("--loop requires --source to be set")
            return
        print(f"\n=== Running repair loop for {args.source} ===")
        run_repair_loop(
            source=args.source,
            run_id=args.run_id,
            max_patches=args.max_patches,
        )
        return

    if args.patch:
        if not args.source:
            print("--patch requires --source to be set")
            return
        run_agent_repair(args.source, selectors=args.selectors)
        return

    if args.all:
        repair_all()
    elif args.source:
        repair_for_source(args.source)
    else:
        print("Specify --source name or use --all, --patch, or --loop")


if __name__ == "__main__":
    main()
