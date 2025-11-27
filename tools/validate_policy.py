# file: tools/validate_policy.py
"""
CLI to validate OpenFeature / rollout policies.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.governance import openfeature_flags


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate feature-flag / rollout policies.")
    parser.add_argument("path", type=str, help="Path to a JSON policy file.")
    args = parser.parse_args()

    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    # This assumes you extend openfeature_flags with a validate() later.
    if hasattr(openfeature_flags, "validate"):
        ok = openfeature_flags.validate(data)  # type: ignore[attr-defined]
    else:
        ok = True

    print(json.dumps({"ok": ok}, indent=2))


if __name__ == "__main__":
    main()
