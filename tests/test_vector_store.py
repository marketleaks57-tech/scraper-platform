import json
import math

from src.governance.openfeature import override_flags
from src.processors import vector_store as vector_store_module
from src.processors.pcid_matcher import (
    build_pcid_index,
    build_vector_store,
    load_pcid_master,
    match_pcid,
    match_pcid_with_confidence,
    persist_pcid_mappings,
)
from src.processors.vector_store import PCIDVectorStore


def test_vector_store_similarity_and_threshold():
    store = PCIDVectorStore(dims=16)
    store.add("PCID-1", [1.0] * 16, metadata={"source": "alpha"})
    store.add("PCID-2", [0.0] * 15 + [math.sqrt(2)], metadata={"source": "beta"})

    results = store.query([1.0] * 16, top_k=2, threshold=0.1)
    assert results[0]["pcid"] == "PCID-1"
    assert len(results) == 2
    assert results[0]["score"] > results[1]["score"]

    filtered = store.query([0.0] * 16, threshold=0.9)
    assert filtered == []


def test_match_pcid_fallback_to_vector_store():
    store = PCIDVectorStore(dims=8)
    store.populate_from_records(
        [
            {"pcid": "PCID-A", "name": "Widget", "company": "ACME", "currency": "USD"},
            {"pcid": "PCID-B", "name": "Gadget", "company": "Beta Labs", "currency": "USD"},
        ]
    )

    index = {("widget", "acme", "usd"): "PCID-A"}

    # Exact match succeeds
    record = {"name": "Widget", "company": "ACME", "currency": "USD"}
    assert match_pcid(record, index, vector_store=store) == "PCID-A"

    # No exact key match, but vector search finds closest PCID
    fuzzy_record = {"name": "Gadget Kit", "company": "Beta Labs", "currency": "USD"}
    assert match_pcid(fuzzy_record, {}, vector_store=store, min_similarity=0.1) == "PCID-B"


def test_match_pcid_with_confidence_tracks_score():
    store = PCIDVectorStore(dims=8)
    store.populate_from_records(
        [
            {"pcid": "PCID-B", "name": "Gadget", "company": "Beta Labs", "currency": "USD"},
        ]
    )

    record = {"name": "Gadget Kit", "company": "Beta Labs", "currency": "USD"}
    pcid, score = match_pcid_with_confidence(record, {}, vector_store=store, min_similarity=0.1)
    assert pcid == "PCID-B"
    assert score > 0.1


def test_match_pcid_uses_remote_backend(monkeypatch):
    called = {}

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_post(url, json, timeout):
        called["url"] = url
        called["payload"] = json
        called["timeout"] = timeout
        return DummyResponse({"matches": [{"pcid": "PCID-REMOTE", "score": 0.92}]})

    monkeypatch.setenv("PCID_VECTOR_STORE_URL", "http://pcid-backend")
    monkeypatch.setattr(vector_store_module.requests, "post", fake_post)

    record = {"name": "Widget", "company": "ACME", "currency": "USD"}
    pcid_index = {}

    assert match_pcid(record, pcid_index) == "PCID-REMOTE"
    assert called["url"] == "http://pcid-backend/query"
    assert called["payload"]["record"] == record
    assert called["payload"]["threshold"] == 0.8


def test_match_pcid_remote_backend_gated(monkeypatch):
    called = {}

    class DummyResponse:
        def raise_for_status(self):
            called["raised"] = True

        def json(self):
            return {"matches": [{"pcid": "PCID-REMOTE", "score": 0.9}]}

    def fake_post(url, json, timeout):
        called["url"] = url
        return DummyResponse()

    monkeypatch.setenv("PCID_VECTOR_STORE_URL", "http://pcid-backend")
    monkeypatch.setattr(vector_store_module.requests, "post", fake_post)

    record = {"name": "Widget", "company": "ACME", "currency": "USD"}
    with override_flags({"pcid.vector_store.remote_backend": False}):
        assert match_pcid(record, {}) is None
        assert called == {}

    # When similarity fallback itself is disabled, no vector-store call is made.
    store = PCIDVectorStore(dims=8)
    store.populate_from_records(
        [{"pcid": "PCID-A", "name": "Widget", "company": "ACME", "currency": "USD"}]
    )
    with override_flags({"pcid.vector_store.similarity_fallback": False}):
        assert match_pcid({"name": "Widget"}, {}, vector_store=store) is None


def test_pcid_master_load_index_and_persist(tmp_path):
    master_path = tmp_path / "pcid_master.jsonl"
    records = [
        {"pcid": "PCID-XYZ", "name": "Widget", "company": "ACME", "currency": "USD"},
        {"pcid": "PCID-ABC", "name": "Gadget", "company": "Beta Labs", "currency": "USD"},
    ]
    master_path.write_text("\n".join(json.dumps(rec) for rec in records), encoding="utf-8")

    loaded = load_pcid_master(master_path)
    assert len(loaded) == 2

    index = build_pcid_index(loaded)
    store = build_vector_store(loaded, dims=8)

    pcid, score = match_pcid_with_confidence(
        {"name": "Widget", "company": "ACME", "currency": "USD"}, index, vector_store=store
    )
    assert pcid == "PCID-XYZ"
    assert score == 1.0

    mappings_path = tmp_path / "mappings.jsonl"
    persist_pcid_mappings(
        [
            {"product_url": "http://example.com/widget", "pcid": pcid, "confidence": score, "source": "alfabeta"}
        ],
        mappings_path,
    )

    persisted = mappings_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(persisted) == 1
    assert "PCID-XYZ" in persisted[0]
