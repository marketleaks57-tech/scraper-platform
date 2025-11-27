from unittest import mock

from src.orchestration.batch import BatchOrchestrator


@mock.patch("src.orchestration.batch.run_pipeline", autospec=True)
def test_batch_orchestrator_runs_each_source(mock_run):
    mock_run.return_value = {"status": "success", "run_id": "1"}
    orchestrator = BatchOrchestrator(["alpha", "beta"])
    results = orchestrator.run(environment="dev")
    assert len(results) == 2
    mock_run.assert_any_call(source="alpha", run_type="FULL_REFRESH", environment="dev", params={})
    mock_run.assert_any_call(source="beta", run_type="FULL_REFRESH", environment="dev", params={})

