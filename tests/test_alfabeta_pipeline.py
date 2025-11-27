import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engines.selenium_engine import FakeDriver
from src.scrapers.alfabeta.alfabeta_full_impl import extract_product
from src.scrapers.alfabeta.company_index import fetch_company_urls
from src.scrapers.alfabeta.pipeline import run_alfabeta
from src.scrapers.alfabeta.product_index import fetch_product_urls


def test_company_and_product_discovery_uses_samples(tmp_path, monkeypatch):
    driver = FakeDriver()
    base_url = "https://example.com/companies"
    selectors = {}

    companies = fetch_company_urls(driver, base_url, selectors, run_id="test")
    assert len(companies) == 2
    assert companies[0].startswith("https://example.com/company")

    products = fetch_product_urls(driver, companies[0], selectors, run_id="test")
    assert len(products) == 2
    assert products[0].startswith(companies[0])


def test_extract_product_from_sample(monkeypatch):
    driver = FakeDriver()
    record = extract_product(driver, "https://example.com/company/acme/product/alpha", selectors={}, run_id="test")
    assert record["name"] == "Alpha Med"
    assert record["price"] == 123.45
    assert record["currency"] == "ARS"


def test_run_alfabeta_end_to_end(monkeypatch, tmp_path):
    # Ensure fake browser + accounts
    monkeypatch.setenv("SCRAPER_PLATFORM_FAKE_BROWSER", "1")
    monkeypatch.setenv("ALFABETA_USER_1", "demo")
    monkeypatch.setenv("ALFABETA_PASS_1", "demo-pass")
    monkeypatch.setenv("SCRAPER_SECRET_KEY", "cJJS2KEJeyfjovwfsMboxchO5s-uWq-XzXjt6Uh85fU=")

    # Isolate output directory
    monkeypatch.setenv("SCRAPER_PLATFORM_VERSION", "4.9.0-test")

    output_path = run_alfabeta()
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) >= 2  # header + at least one row

    # Clean up after test to keep workspace tidy
    output_path.unlink(missing_ok=True)
