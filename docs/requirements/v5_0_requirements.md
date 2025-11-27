# v5.0 Requirements

- Decide the canonical agent orchestrator and mark the alternative as experimental or deprecated.
- Implement or explicitly disable browser engines in `src/pipeline_pack/engines/`.
- Harden optional dependency handling so HTTP-only deployments do not fail when `psycopg2` or `selenium` are absent.
- Finalize production readiness checklist: database connectivity, monitoring, and pipeline validation per target source.
