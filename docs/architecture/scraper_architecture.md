# Scraper Architecture

This scraper platform separates concerns across agents, engines, processors, and exporters to keep pipelines composable.

## Agents
- Legacy agents under `src/agents/` remain the canonical orchestrator for v5.0.
- Pipeline-pack agents in `src/pipeline_pack/agents/` mirror core behaviors and are marked experimental until browser engines are complete.

## Engines
- **HTTP engine** in `src/pipeline_pack/engines/http_engine.py` is stable.
- **Browser engines** (`playwright_engine.py`, `selenium_engine.py`) are skeletal; disable or implement before use.

## Processors and exporters
- Processor helpers (LLM normalization, PCID matching, QC rules) live in `src/pipeline_pack/processors/`.
- Exporters target CSV, JSON, or databases via `src/pipeline_pack/exporters/`.

## Frontend and APIs
- `frontend-dashboard/` provides observability into runs, exports, and proxy health.
- API routes surface run control and monitoring; keep optional dependencies lazy to avoid startup failures.
