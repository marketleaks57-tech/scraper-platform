#!/usr/bin/env python3
"""
Load proxy credentials into the platform cache/DB using src.resource_manager APIs.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import yaml

from src.common import settings
from src.resource_manager.proxy_pool import ProxyPool


def _load_config(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Proxy config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data.get("per_source_overrides") or data.get("proxies") or data


def bootstrap(config_path: Path) -> None:
    config = _load_config(config_path)
    pool = ProxyPool({"proxies": config})
    for source, proxies in config.items():
        if not proxies:
            continue
        chosen = pool.choose_proxy(source)
        print(f"[bootstrap] {source}: {len(proxies)} proxies registered; sample={chosen}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap proxies into the pool")
    parser.add_argument(
        "--config",
        default=Path("config/proxies.yaml"),
        type=Path,
        help="Path to proxy definition JSON file",
    )
    args = parser.parse_args()

    settings.bootstrap()
    bootstrap(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

