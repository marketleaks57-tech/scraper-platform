import os

import pytest

from src.versioning.version_manager import (
    PLATFORM_VERSION,
    VersionInfo,
    attach_version_metadata,
    build_version_info,
    get_platform_version,
)


def test_get_platform_version_defaults(monkeypatch):
    monkeypatch.delenv("SCRAPER_PLATFORM_VERSION", raising=False)
    assert get_platform_version() == PLATFORM_VERSION


def test_get_platform_version_env_override(monkeypatch):
    monkeypatch.setenv("SCRAPER_PLATFORM_VERSION", "9.9.9")
    assert get_platform_version() == "9.9.9"


def test_build_version_info_and_attach():
    version = build_version_info(
        "alfabeta",
        scraper_version="1.2.3",
        schema_version="2024-10-01",
        selectors_version="abc123",
        code_commit="deadbeef",
    )
    assert isinstance(version, VersionInfo)
    assert version.platform == get_platform_version()

    record = {"name": "product", "price": 10}
    enriched = attach_version_metadata(record, version)

    assert record is not enriched
    assert enriched["_version"]["scraper"] == "alfabeta"
    assert enriched["_version"]["schema_version"] == "2024-10-01"
    assert enriched["_version"]["code_commit"] == "deadbeef"
