from types import SimpleNamespace

import pytest

pytest.importorskip("airflow")

import dags.scraper_alfabeta as alfabeta_dag


def test_resolve_runtime_env_prefers_dag_conf(monkeypatch):
    monkeypatch.delenv("SCRAPER_PLATFORM_ENV", raising=False)
    monkeypatch.delenv("SCRAPER_ENV", raising=False)
    monkeypatch.delenv("ENV", raising=False)

    context = {"dag_run": SimpleNamespace(conf={"env": "dag-env"})}
    assert alfabeta_dag._resolve_runtime_env(context) == "dag-env"


def test_resolve_runtime_env_falls_back_to_env(monkeypatch):
    monkeypatch.delenv("SCRAPER_PLATFORM_ENV", raising=False)
    monkeypatch.delenv("SCRAPER_ENV", raising=False)
    monkeypatch.setenv("ENV", "generic-env")

    assert alfabeta_dag._resolve_runtime_env({}) == "generic-env"


def test_run_pipeline_executes_via_kernel(monkeypatch):
    captured = {}

    def fake_run_alfabeta(env=None):
        captured["env"] = env
        return "/tmp/alfabeta-output.csv"

    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("SCRAPER_PLATFORM_ENV", "prod-dsl")
    # Stub the actual scraper entrypoint so the DAG executes quickly
    import src.scrapers.alfabeta.pipeline as pipeline

    monkeypatch.setattr(pipeline, "run_alfabeta", fake_run_alfabeta)

    # Execute with an empty dag_run to exercise env fallback + DSL execution
    result = alfabeta_dag._run_alfabeta_pipeline(dag_run=None)

    assert result == "/tmp/alfabeta-output.csv"
    assert captured["env"] == "prod-dsl"

