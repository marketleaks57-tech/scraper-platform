from __future__ import annotations

import pytest

from src.etl.bigquery_loader import load_to_bigquery
from src.etl.kafka_producer import publish_records
from src.etl.snowflake_loader import load_to_snowflake


def _failing_iter():
    raise RuntimeError("boom")
    yield  # pragma: no cover


def test_etl_stubs_return_counts_on_dry_run():
    records = [{"id": 1}, {"id": 2}]
    assert load_to_bigquery("dataset.table", records, dry_run=True) == 2
    assert load_to_snowflake("table", records, dry_run=True) == 2
    assert publish_records("topic", records, dry_run=True) == 2


def test_etl_stubs_swallow_iterator_errors():
    for func in (load_to_bigquery, load_to_snowflake, publish_records):
        assert func("dest", _failing_iter()) == 0
