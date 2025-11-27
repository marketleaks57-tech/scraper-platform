import pytest

from src.agents import agent_orchestrator
from src.agents.deepagent_repair_engine import run_repair_session
from src.agents.deepagent_selector_healer import propose_selector_patches


def test_propose_selector_patches_uses_class_match():
    selectors = {"title": {"css": "#title"}}
    old_html = "<h1 id='title' class='headline'>Foo Product</h1>"
    new_html = "<h1 class='headline'>Foo Product</h1>"

    patches = propose_selector_patches(old_html, new_html, selectors)
    assert len(patches) == 1
    assert patches[0].new_selector == "h1.headline"


def test_run_repair_session_applies_patch(monkeypatch, tmp_path):
    snapshots_dir = tmp_path / "alfabeta"
    snapshots_dir.mkdir(parents=True)
    (snapshots_dir / "20240101_old.html").write_text("<h1 id='title'>Old</h1>", encoding="utf-8")
    (snapshots_dir / "20240102_new.html").write_text("<h1 class='headline'>Old</h1>", encoding="utf-8")

    selectors_path = tmp_path / "selectors.json"
    selectors_path.write_text('{"title": {"css": "#title"}}', encoding="utf-8")

    monkeypatch.setattr("src.agents.deepagent_repair_engine.REPLAY_SNAPSHOTS_DIR", tmp_path)

    results = run_repair_session("alfabeta", selectors_path=selectors_path)
    assert results
    saved = selectors_path.read_text(encoding="utf-8")
    assert "contains('Old')" in saved


def test_orchestrator_triggers_repair(monkeypatch):
    calls = {}

    def _fake_repair(source, selectors_path=None):
        calls["source"] = source
        return [object()]

    monkeypatch.setattr(agent_orchestrator, "run_repair_session", _fake_repair)

    outcome = agent_orchestrator.orchestrate_source_repair(
        source="alfabeta",
        baseline_rows=100,
        current_rows=40,
        validation_rate=0.5,
    )

    assert calls["source"] == "alfabeta"
    assert outcome.triggered_repair

