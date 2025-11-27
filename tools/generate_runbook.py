# file: tools/generate_runbook.py
"""
CLI to generate a markdown runbook for a given source.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.common.config_loader import load_source_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a markdown runbook for a source.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True, help="Output .md file.")
    args = parser.parse_args()

    cfg = load_source_config(args.source)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Runbook – {args.source}",
        "",
        "## Config snapshot",
        "",
        "```yaml",
        repr(cfg),
        "```",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
