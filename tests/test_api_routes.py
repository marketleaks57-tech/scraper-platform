from datetime import datetime

from src.api.routes import runs, source_health, steps
from src.scheduler import scheduler_db_adapter as db


def test_routes_registered_on_app():
    # Build from module router definitions to avoid importing TestClient (which needs httpx)
    assert any(route.path == "/api/runs" for route in runs.router.routes)
    assert any(route.path == "/api/runs/{run_id}" for route in runs.router.routes)
    assert any(route.path == "/api/steps/{run_id}" for route in steps.router.routes)
    assert any(route.path == "/api/source-health" for route in source_health.router.routes)


def test_runs_endpoint_returns_fallback_when_db_empty(monkeypatch):
    monkeypatch.setattr(db, "fetch_run_summaries", lambda: [])

    payload = [run.model_dump() for run in runs.get_runs()]
    # Fallback dataset contains three runs for the dashboard
    assert len(payload) == 3
    assert {run["id"] for run in payload} == {
        "run_2024_001",
        "run_2024_002",
        "run_2024_003",
    }


def test_run_detail_prefers_db_rows(monkeypatch):
    db_detail = db.RunDetailRow(
        run_id="db_run",
        source="alfabeta",
        status="success",
        started_at=datetime(2024, 5, 1, 10, 0),
        duration_seconds=12,
        finished_at=datetime(2024, 5, 1, 10, 1),
        stats={"products": 1},
        metadata={"version": "1.0"},
    )
    db_steps = [
        db.RunStepRow(
            step_id="s1",
            name="company_index",
            status="success",
            started_at=datetime(2024, 5, 1, 10, 0),
            duration_seconds=6,
        )
    ]

    monkeypatch.setattr(db, "fetch_run_detail", lambda run_id: db_detail if run_id == "db_run" else None)
    monkeypatch.setattr(db, "fetch_run_steps", lambda run_id: db_steps if run_id == "db_run" else [])

    payload = runs.get_run("db_run").model_dump()
    assert payload["metadata"]["version"] == "1.0"
    assert payload["stats"]["products"] == 1
    assert payload["steps"][0]["id"] == "s1"


def test_run_detail_falls_back_to_static(monkeypatch):
    monkeypatch.setattr(db, "fetch_run_detail", lambda run_id: None)
    monkeypatch.setattr(db, "fetch_run_steps", lambda run_id: [])

    payload = runs.get_run("run_2024_001").model_dump()
    assert payload["id"] == "run_2024_001"
    assert payload["source"] == "alfabeta"
    assert payload["steps"]


def test_steps_endpoint_uses_db_when_available(monkeypatch):
    db_steps = [
        db.RunStepRow(
            step_id="db_step",
            name="company_index",
            status="success",
            started_at=datetime(2024, 5, 1, 10, 0),
            duration_seconds=5,
        )
    ]
    monkeypatch.setattr(db, "fetch_run_steps", lambda run_id: db_steps if run_id == "db_run" else [])

    payload = [step.model_dump() for step in steps.get_steps("db_run")]
    assert payload[0]["id"] == "db_step"


def test_source_health_fallback(monkeypatch):
    monkeypatch.setattr(db, "fetch_source_metrics", lambda: [])
    payload = [health.model_dump() for health in source_health.get_source_health()]
    assert len(payload) == 2
