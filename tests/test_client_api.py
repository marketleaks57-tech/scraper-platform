import json
from unittest.mock import Mock

import pytest
from requests import Response

from src.client_api import ClientAPIError, HealthClient, ScraperClient


def _make_response(payload, status: int = 200, content_type: str = "application/json") -> Response:
    resp = Response()
    resp.status_code = status
    resp._content = json.dumps(payload).encode("utf-8")
    resp.headers["Content-Type"] = content_type
    return resp


def test_scraper_client_parses_run_models():
    session = Mock()
    session.request.side_effect = [
        _make_response(
            [
                {"id": "run-1", "source": "alfabeta", "status": "succeeded", "startedAt": "2024-05-01T00:00:00Z"}
            ]
        ),
        _make_response(
            {
                "id": "run-1",
                "source": "alfabeta",
                "status": "succeeded",
                "startedAt": "2024-05-01T00:00:00Z",
                "finishedAt": "2024-05-01T00:10:00Z",
                "durationSeconds": 600,
                "steps": [
                    {
                        "id": "step-1",
                        "name": "fetch",
                        "status": "ok",
                        "startedAt": "2024-05-01T00:00:00Z",
                        "durationSeconds": 120,
                    }
                ],
            }
        ),
        _make_response(
            [
                {
                    "id": "step-1",
                    "name": "fetch",
                    "status": "ok",
                    "startedAt": "2024-05-01T00:00:00Z",
                    "durationSeconds": 120,
                }
            ]
        ),
    ]

    client = ScraperClient("http://localhost", session=session)

    runs = client.list_runs()
    assert runs[0].id == "run-1"
    assert runs[0].source == "alfabeta"

    detail = client.get_run("run-1")
    assert detail.finishedAt is not None
    assert detail.steps[0].name == "fetch"

    steps = client.get_steps("run-1")
    assert steps[0].id == "step-1"

    # three requests should have been issued in order
    assert session.request.call_count == 3


def test_health_client_sources(monkeypatch):
    session = Mock()
    session.request.side_effect = [
        _make_response({"status": "ok"}),
        _make_response(
            [
                {
                    "source": "alfabeta",
                    "status": "healthy",
                    "lastRunAt": "2024-05-01T10:00:00Z",
                    "consecutiveFailures": 0,
                    "budgetExhausted": False,
                }
            ]
        ),
    ]

    client = HealthClient("http://localhost", session=session)
    assert client.health() is True

    health = client.source_health()
    assert health[0].source == "alfabeta"
    assert session.request.call_count == 2


def test_client_error_propagates_status():
    session = Mock()
    session.request.return_value = _make_response({"error": "boom"}, status=500)
    client = ScraperClient("http://localhost", session=session)

    with pytest.raises(ClientAPIError) as excinfo:
        client.list_runs()

    assert excinfo.value.status_code == 500
    assert "boom" in excinfo.value.response_body
