from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.versioning import schema_registry as reg
from src.versioning.version_manager import (
    SNAPSHOT_DIR,
    SnapshotRecord,
    VersionInfo,
    VersionPolicy,
    attach_version_metadata,
    build_version_info,
    register_version,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    reg._SCHEMA_REGISTRY.clear()  # type: ignore[attr-defined]
    yield
    reg._SCHEMA_REGISTRY.clear()  # type: ignore[attr-defined]


def test_register_version_persists_snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr("src.versioning.version_manager.SNAPSHOT_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)

    version = build_version_info("alfabeta", scraper_version="1.0.0")
    snapshot: SnapshotRecord = register_version(
        source="alfabeta",
        run_id="run-123",
        version=version,
        schema_name="product_record",
        selectors_payload={"name": "div.title"},
    )

    assert snapshot.path.exists()
    data = json.loads(Path(snapshot.path).read_text())
    assert data["schema_signature"] == snapshot.schema_signature
    assert data["selectors_signature"] == snapshot.selectors_signature
    assert data["version"]["scraper_version"] == "1.0.0"


def test_register_version_detects_schema_drift(tmp_path, monkeypatch):
    monkeypatch.setattr("src.versioning.version_manager.SNAPSHOT_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)

    version = VersionInfo(platform="p", scraper="s")
    register_version(
        source="s",
        run_id="r1",
        version=version,
        schema_name="product_record",
    )

    # Overwrite schema to force drift
    reg.register_schema("product_record", {"required_fields": ["only_one"]})
    with pytest.raises(ValueError):
        register_version(
            source="s",
            run_id="r2",
            version=version,
            schema_name="product_record",
            version_policy=VersionPolicy(keep_history=False),
        )


def test_attach_version_metadata_adds_version_block():
    version = VersionInfo(platform="p", scraper="s")
    enriched = attach_version_metadata({"k": "v"}, version)
    assert enriched["_version"]["platform"] == "p"
    assert enriched["k"] == "v"
