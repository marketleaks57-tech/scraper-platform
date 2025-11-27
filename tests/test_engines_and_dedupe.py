import asyncio

import pytest

from src.engines import playwright_engine as pe
from src.engines import selenium_engine as se
from src.processors.dedupe import dedupe_records
from src.processors.unify_fields import unify_record


class _DummySessionRecord:
    def __init__(self):
        self.restored = 0

    def try_restore_cookies(self, _driver):
        self.restored += 1

    def save_cookies(self, _driver):
        return None


class _FlakyDriver:
    def __init__(self, fail_times: int = 1):
        self.fail_times = fail_times
        self.calls = 0
        self.current_url = ""
        self.page_source = ""

    def get(self, url: str):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise se.WebDriverException("429 Too Many Requests")
        self.current_url = url
        self.page_source = "ok"

    def quit(self):
        return None


def test_selenium_navigate_retries_and_proxy_failover(monkeypatch):
    created = []

    def _fake_create_driver(proxy=None):
        created.append(proxy)
        # Fail only while a proxy is provided; succeed once fallback happens.
        return _FlakyDriver(fail_times=1 if proxy else 0)

    monkeypatch.setattr(se, "create_driver", _fake_create_driver)

    session_record = _DummySessionRecord()
    driver = _fake_create_driver(proxy="proxy:1")
    browser = se.BrowserSession(driver, session_record, proxy="proxy:1")

    browser.navigate("http://example.com", retries=3, backoff=0.01, jitter=0.0, wait=0.0)

    assert browser.driver.current_url == "http://example.com"
    # Proxy driver + fallback driver were created
    assert created[0] == "proxy:1"
    assert created[-1] is None
    assert session_record.restored >= 1


class _FlakyPage:
    def __init__(self):
        self.calls = 0
        self.waits = []
        self.url = None
        self.html = "<html></html>"

    async def goto(self, url: str):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("429")
        self.url = url

    async def wait_for_timeout(self, ms: int):
        self.waits.append(ms)

    async def content(self):
        return self.html


def test_playwright_goto_retries_with_jitter():
    page = _FlakyPage()
    asyncio.run(
        pe.goto_with_retry(
            page,
            "http://example.com",
            retries=2,
            backoff=0.01,
            jitter=0.0,
            wait_ms=5,
        )
    )
    assert page.calls == 2
    assert page.url == "http://example.com"
    assert page.waits  # ensure waits were used


def test_dedupe_records_drops_duplicates():
    records = [
        {"product_url": "a", "name": "x", "price": 1},
        {"product_url": "a", "name": "x", "price": 1},
        {"product_url": "b", "name": "y", "price": 2},
    ]

    unique = dedupe_records(records)
    assert len(unique) == 2
    assert unique[0]["product_url"] == "a"
    assert unique[1]["product_url"] == "b"


def test_unify_record_maps_item_url_and_source():
    raw = {
        "item_url": "http://example.com/1",
        "name": "Example",
        "price": "2.5",
        "currency": "USD",
        "company": "ACME",
        "source": "unit-test",
    }

    unified = unify_record(raw)

    assert unified["product_url"] == "http://example.com/1"
    assert unified["price"] == 2.5
    assert unified["company"] == "ACME"
    assert unified["source"] == "unit-test"
