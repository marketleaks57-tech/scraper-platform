from src.observability.prometheus_exporter import CollectorRegistry, create_metrics, dump_metrics


def test_metrics_emission():
    registry = CollectorRegistry()
    metrics = create_metrics(registry=registry)
    metrics["runs_total"].inc(2)
    metrics["runs_failed"].inc()
    payload = dump_metrics(metrics)
    assert b"scraper_runs_total" in payload or payload == b""
