# LLM Integration and Status

Guidance, quick references, and current status for integrating LLM-driven steps into scraping pipelines.

## Integration Guidelines
- Isolate LLM calls in dedicated agents/processors for clarity and easier troubleshooting.
- Log prompts and responses when allowed for debugging.
- Provide configuration flags to disable LLM usage per environment.
- Refer to `config/agents/defaults.yaml` for global settings and update as integrations grow.

## Components
- `src/pipeline_pack/agents/llm_normalizer_agent.py`
- `src/pipeline_pack/processors/llm_normalizer.py`

## Configuration
- Configure LLM behavior via agent configs in `config/agents/defaults.yaml` or source-specific overrides.

## Current Status
- LLM normalization agent available; testing recommended before production use.
- No other LLM-based agents are enabled by default.
- Track future LLM integrations and evaluation results here.
