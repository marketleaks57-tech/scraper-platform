from __future__ import annotations

from src.tests_replay import replay_runner, snapshot_loader
from src.tests_replay.history_replay import replay_history


def _write_snapshot(base, name, html):
    path = base / f"{name}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def test_replay_history_detects_schema_drift_and_diff(tmp_path, monkeypatch):
    monkeypatch.setattr(snapshot_loader, "REPLAY_SNAPSHOTS_DIR", tmp_path)

    base = tmp_path / "demo" / "daily"
    _write_snapshot(base, "001", "<html><body><div>one</div></body></html>")
    _write_snapshot(base, "002", "<html><body><div>one</div><p>two</p></body></html>")

    results = replay_history("demo", "daily", diff_context=1)

    assert len(results) == 2
    assert results[0].schema_drift is False
    assert results[1].schema_drift is True
    assert "<p>two" in (results[1].diff or "")


def test_replay_runner_cli_outputs_diff(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(snapshot_loader, "REPLAY_SNAPSHOTS_DIR", tmp_path)
    monkeypatch.setattr(replay_runner, "REPLAY_SNAPSHOTS_DIR", tmp_path)

    base = tmp_path / "demo"
    _write_snapshot(base, "old", "<html><body><h1>Old</h1></body></html>")
    _write_snapshot(base, "new", "<html><body><h1>New</h1><section>extra</section></body></html>")

    replay_runner.main(["demo", "--diff", "--context", "1"])

    output = capsys.readouterr().out
    assert "Found 2 snapshots" in output
    assert "schema drift" in output
    assert "<h1>New" in output
