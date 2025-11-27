# file: tools/approve_patch.py
"""
CLI for approving DeepAgent-generated patches.
"""

from __future__ import annotations

import argparse

from src.agents import agent_api  # type: ignore[import]


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve and optionally apply a DeepAgent patch.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--apply", action="store_true", help="Apply the patch instead of dry-run.")
    args = parser.parse_args()

    result = agent_api.run_auto_heal(args.run_id, args.source, dry_run=not args.apply)
    print(result)


if __name__ == "__main__":
    main()
