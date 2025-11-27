from src.validation import check_required_fields, dedupe_by_keys, ensure_currency_consistency


def test_check_required_fields_flags_missing():
    records = [{"pcid": "1", "price": 10}, {"pcid": None, "price": 5}]
    failures = check_required_fields(records, ["pcid", "price"])
    assert len(failures) == 1
    assert failures[0]["missing"] == ["pcid"]


def test_dedupe_by_keys_removes_duplicates():
    records = [{"pcid": "1"}, {"pcid": "1"}, {"pcid": "2"}]
    deduped = dedupe_by_keys(records, ["pcid"])
    assert len(deduped) == 2


def test_currency_consistency_detects_violation():
    records = [{"currency": "USD"}, {"currency": "CAD"}]
    violations = ensure_currency_consistency(records, "USD")
    assert len(violations) == 1

