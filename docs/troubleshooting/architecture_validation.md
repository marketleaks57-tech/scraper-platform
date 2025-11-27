# Architecture Validation

This document tracks checkpoints used to validate the scraper platform architecture. For detailed diagrams and component descriptions, refer to `../architecture/system_overview.md`.

## Current status
- Core agent orchestrator (`src/agents/orchestrator.py`) validated for v5.0 flows.
- Pipeline pack orchestrator (`src/pipeline_pack/agents/orchestrator.py`) available for experimental runs; see `../misc/documentation_index.md` for context.
- Airflow DAGs parse successfully in CI; ensure new DAGs reference the correct orchestrator.

## Next steps
- Update this file after architecture changes or when promoting the experimental pipeline pack to primary.
