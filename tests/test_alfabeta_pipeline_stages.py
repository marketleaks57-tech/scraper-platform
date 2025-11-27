import sys
from datetime import datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engines.selenium_engine import FakeDriver
from src.scrapers.alfabeta.pipeline import (
    PipelineContext,
    export_records,
    fetch_details,
    fetch_listings,
    match_pcid,
    normalize_records,
    parse_raw,
    run_qc,
)
from src.versioning.version_manager import build_version_info


@pytest.fixture()
def pipeline_ctx(monkeypatch, tmp_path):
    ctx = PipelineContext(
        source="alfabeta",
        platform_config={},
        source_config={"schema_name": "product_record"},
        selectors={},
        run_id="test-run",
        version_info=build_version_info("alfabeta", scraper_version="1.0.0", schema_version="1.0.0"),
        driver=FakeDriver(),
        base_url="https://example.com/companies",
        pcid_index={},
        pcid_vector_store=None,
        pcid_min_similarity=0.8,
        baseline_rows=0,
        run_started_at=datetime.utcnow(),
        env="test",
        output_dir=tmp_path,
    )

    monkeypatch.setenv("SCRAPER_PLATFORM_FAKE_BROWSER", "1")
    monkeypatch.setattr(
        "src.scrapers.alfabeta.pipeline.run_recorder.record_step",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "src.scrapers.alfabeta.pipeline.run_recorder.finish_run",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "src.scrapers.alfabeta.pipeline.record_run_cost",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "src.scrapers.alfabeta.pipeline.orchestrate_source_repair",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "src.scrapers.alfabeta.pipeline.persist_pcid_mappings",
        lambda *args, **kwargs: None,
    )
    return ctx


def test_fetch_listings_returns_companies(pipeline_ctx):
    listings = fetch_listings(pipeline_ctx)
    assert len(listings) == 2
    assert listings[0].startswith("https://example.com/company")


def test_fetch_details_returns_product_urls(pipeline_ctx):
    listings = fetch_listings(pipeline_ctx)
    details = fetch_details(pipeline_ctx, listings)
    assert len(details) == 4
    assert all(url.startswith("https://example.com/company") for url in details)


def test_parse_raw_extracts_products(pipeline_ctx):
    details = fetch_details(pipeline_ctx, fetch_listings(pipeline_ctx))
    parsed = parse_raw(pipeline_ctx, details)
    assert parsed
    assert parsed[0]["name"] == "Alpha Med"


def test_normalize_records_enriches_metadata(pipeline_ctx):
    parsed = parse_raw(pipeline_ctx, fetch_details(pipeline_ctx, fetch_listings(pipeline_ctx)))
    normalized = normalize_records(pipeline_ctx, parsed)
    assert normalized
    assert normalized[0]["run_id"] == "test-run"
    assert normalized[0]["_version"]


def test_match_pcid_preserves_records(pipeline_ctx):
    normalized = normalize_records(
        pipeline_ctx, parse_raw(pipeline_ctx, fetch_details(pipeline_ctx, fetch_listings(pipeline_ctx)))
    )
    matched = match_pcid(pipeline_ctx, normalized)
    assert matched
    assert all("name" in rec for rec in matched)


def test_run_qc_filters_and_dedupes(pipeline_ctx):
    normalized = normalize_records(
        pipeline_ctx, parse_raw(pipeline_ctx, fetch_details(pipeline_ctx, fetch_listings(pipeline_ctx)))
    )
    matched = match_pcid(pipeline_ctx, normalized)
    qc_records = run_qc(pipeline_ctx, matched)
    assert qc_records
    assert pipeline_ctx.invalid_records == 0


def test_export_records_writes_csv(pipeline_ctx):
    normalized = normalize_records(
        pipeline_ctx, parse_raw(pipeline_ctx, fetch_details(pipeline_ctx, fetch_listings(pipeline_ctx)))
    )
    matched = match_pcid(pipeline_ctx, normalized)
    qc_records = run_qc(pipeline_ctx, matched)
    out_path = export_records(pipeline_ctx, qc_records)
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8").splitlines()
    assert content[0].startswith("product_url,name,price")
