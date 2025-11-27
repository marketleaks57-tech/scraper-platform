#!/usr/bin/env python3
"""
Wrapper script to expose tools.add_scraper_advanced as a top-level CLI.
"""
from tools.add_scraper_advanced import main as tools_main


def main() -> int:
    return tools_main()


if __name__ == "__main__":
    raise SystemExit(main())

