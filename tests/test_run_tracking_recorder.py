from datetime import datetime
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture()
def temp_db(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "runs.db"
    monkeypatch.setenv("RUN_DB_PATH", str(db_path))
    from src.scheduler import scheduler_db_adapter as db

    if db._CONN is not None:
        db._CONN.close()
        db._CONN = None
    return db_path


def test_run_tracking_writes_and_reads_via_api(temp_db):
    from src.run_tracking import recorder
    from src.api.data import run_store

    run_id = "run_tracking_test"
    started_at = datetime.utcnow()

    recorder.start_run(run_id, "alfabeta", metadata={"env": "test"})
    recorder.record_step(
        run_id,
        name="company_index",
        status="success",
        started_at=started_at,
        duration_seconds=3,
    )
    recorder.finish_run(
        run_id,
        source="alfabeta",
        status="success",
        stats={"records": 5, "invalid": 1},
        metadata={"output_path": "out.csv"},
        started_at=started_at,
    )

    summaries = run_store.list_runs()
    assert any(summary.id == run_id and summary.status == "success" for summary in summaries)

    detail = run_store.get_run_detail(run_id)
    assert detail
    assert detail.metadata.get("output_path") == "out.csv"
    assert detail.stats.get("records") == 5
    assert detail.steps
    assert detail.steps[0].name == "company_index"


def test_run_tracking_rolls_back_on_error(temp_db):
    from src.scheduler import scheduler_db_adapter as db
    from src.run_tracking.db_session import get_session

    started_at = datetime.utcnow()
    run_id = "rollback-test"

    with pytest.raises(RuntimeError):
        with get_session() as session:
            db.upsert_run(
                run_id=run_id,
                source="alfabeta",
                status="running",
                started_at=started_at,
                conn=session.conn,
            )
            db.record_run_step(
                step_id="step-1",
                run_id=run_id,
                name="example",
                status="running",
                started_at=started_at,
                conn=session.conn,
            )
            raise RuntimeError("boom")

    conn = sqlite3.connect(temp_db)
    try:
        assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM run_steps").fetchone()[0] == 0
    finally:
        conn.close()
