# Pipeline Flow

The platform executes configurable pipelines defined in YAML. Each pipeline lists ordered agents; the orchestrator builds agents from registry entries and shares context across steps.

## Execution path
1. **Load configuration** from `config/agents/pipelines.yaml` or `config/pipeline_pack/pipelines.yaml` alongside defaults.
2. **Instantiate agents** via the registry; pipeline-pack agents must be registered in `src/pipeline_pack/agents/__init__.py`.
3. **Run steps**: HTTP fetch → HTML parse → normalization/quality control → export.
4. **Emit outputs** to database or file exporters and surface run state to the dashboard and logs.

## Compatibility
Pipelines can reference agents using either `name` or `agent` keys. This preserves backward compatibility while the platform converges on a single orchestrator strategy.
