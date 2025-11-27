import pytest

from src.processors.qc import rules


@pytest.fixture
def base_record():
    return {
        "source": "unit-test",
        "country": "US",
        "product_url": "http://example.com/product/1",
        "name": "Example product",
        "company": "Example Co",
        "price": "1.23",
        "currency": "USD",
    }


def test_price_sanity_fails_on_non_numeric_price(base_record):
    bad_record = dict(base_record)
    bad_record["price"] = "abc"

    overall_pass, results = rules.run_qc_for_record(
        bad_record, rules.get_default_ruleset()
    )

    assert not overall_pass
    price_rule = next(r for r in results if r.rule_id == "price_sanity")
    assert not price_rule.passed
    assert "valid number" in price_rule.message
