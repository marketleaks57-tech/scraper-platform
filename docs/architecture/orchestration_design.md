# Orchestration Design

Two orchestrator tracks exist while migration completes:

- **Legacy orchestrator (`src/agents/orchestrator.py`)**: Canonical for production. Pipelines in `config/agents/pipelines.yaml` use the `agent` key.
- **Pipeline-pack orchestrator (`src/pipeline_pack/agents/orchestrator.py`)**: Experimental. Accepts `name` or `agent` keys and depends on registrations in `src/pipeline_pack/agents/__init__.py`.

## Design notes
- Agent registry (`src/pipeline_pack/agents/registry.py`) resolves agent classes and builds them with shared context.
- YAML defaults are cached per process to limit disk reads; update and reload when configs change.
- Browser engines should be gated behind explicit configuration and dependency checks to avoid runtime crashes.

## Logging and observability
- Emit step names in orchestrator logs to trace slow or failing stages.
- Surface run states to the dashboard and Airflow task logs for triage.
