"""
dump_snapshots_stub.py
-----------------------------------
List all stored HTML snapshots (for replay testing and debugging).

Supports:
 - Local filesystem snapshots (default)
 - Prints snapshot type, source, timestamp, file size
 - Optional extraction of <title> from HTML
"""

from pathlib import Path

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

from src.common.paths import REPLAY_SNAPSHOTS_DIR


def parse_snapshot_filename(name: str):
    """
    Expect filename patterns like:
        snapshot_2025-11-20T12-10-33.html
        listing_snapshot_2025-11-20.html
    """
    base = name.replace(".html", "").replace(".htm", "")
    parts = base.split("_", 1)
    if len(parts) == 2:
        ts = parts[1]
        return ts
    return None


def extract_title(html_path: Path) -> str:
    """Try to extract page <title> to help debugging."""
    if not BEAUTIFULSOUP_AVAILABLE:
        return "(BeautifulSoup not available)"
    try:
        text = html_path.read_text(errors="ignore")
        soup = BeautifulSoup(text, "html.parser")
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else "(no title)"
    except Exception:
        return "(parse failed)"


def list_snapshots():
    """List all stored HTML snapshots for replay testing and debugging."""
    print("\n=== Snapshot Storage: %s ===" % REPLAY_SNAPSHOTS_DIR.resolve())

    if not REPLAY_SNAPSHOTS_DIR.exists():
        print("No snapshot directory found.")
        return

    for source_dir in sorted(REPLAY_SNAPSHOTS_DIR.glob("*")):
        if not source_dir.is_dir():
            continue

        source = source_dir.name
        print(f"\n--- Source: {source} ---")

        for typedir in sorted(source_dir.glob("*")):
            if not typedir.is_dir():
                continue

            snapshot_type = typedir.name
            print(f"  > Snapshot Type: {snapshot_type}")

            html_files = list(typedir.glob("*.html"))
            if not html_files:
                print("    (no snapshots)")
                continue

            for html_path in html_files:
                ts = parse_snapshot_filename(html_path.name)
                title = extract_title(html_path)
                size_kb = html_path.stat().st_size / 1024

                print(f"    - File: {html_path.name}")
                print(f"      Timestamp: {ts}")
                print(f"      Size: {size_kb:.2f} KB")
                print(f"      Title: {title}")


def main():
    list_snapshots()
    print("\nDump complete.\n")


if __name__ == "__main__":
    main()
