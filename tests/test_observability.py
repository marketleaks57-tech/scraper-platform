from src.observability import cost_tracking
from src.observability import source_health_api


def test_cost_tracking_persists_to_json_and_db(tmp_path, monkeypatch):
    json_path = tmp_path / "cost.jsonl"
    db_path = tmp_path / "cost.db"

    monkeypatch.setattr(cost_tracking, "COST_LOG_PATH", json_path)
    monkeypatch.setattr(cost_tracking, "COST_DB_PATH", db_path)

    cost_tracking.record_run_cost(
        source="alfabeta",
        run_id="run-1",
        proxy_cost_usd=1.5,
        compute_cost_usd=2.5,
        other_cost_usd=0.5,
    )

    data = json_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(data) == 1

    db_records = cost_tracking.iter_cost_records_from_db()
    assert len(db_records) == 1
    assert db_records[0]["total_usd"] == 4.5


def test_source_health_reads_outputs_and_costs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    csv_path = output_dir / "alfabeta" / "daily" / "2024-01-01.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text("header\nrow1\nrow2\n", encoding="utf-8")

    json_path = tmp_path / "cost.jsonl"
    db_path = tmp_path / "cost.db"
    monkeypatch.setattr(cost_tracking, "COST_LOG_PATH", json_path)
    monkeypatch.setattr(cost_tracking, "COST_DB_PATH", db_path)
    cost_tracking.record_run_cost(
        source="alfabeta",
        run_id="run-2",
        proxy_cost_usd=2.0,
        compute_cost_usd=1.0,
    )

    monkeypatch.setattr(source_health_api, "OUTPUT_DIR", output_dir)
    health = source_health_api.get_source_health("alfabeta")

    assert health.last_output_file.endswith("2024-01-01.csv")
    assert health.last_output_rows == 2
    assert abs((float(health.last_cost_usd or 0) - 3.0)) < 1e-6
