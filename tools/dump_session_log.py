"""
Dump the raw session_events.jsonl file to stdout in a readable way.
"""

import json

from src.common.paths import SESSION_LOGS_DIR


def main():
    """Dump session events log in a human-readable format."""
    log_file = SESSION_LOGS_DIR / "session_events.jsonl"
    if not log_file.exists():
        print("No session log file found at:", log_file)
        return

    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            print(f"[{ev.get('ts')}] {ev.get('source')} acc={ev.get('account_id')} "
                  f"proxy={ev.get('proxy_id')} type={ev.get('event_type')} extra={ev.get('extra')}")

if __name__ == "__main__":
    main()
