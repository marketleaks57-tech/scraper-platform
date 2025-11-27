# LLM Flow

LLM-driven steps normalize scraped content and enrich fields when configured.

## Components
- **LLM normalizer agent**: `src/pipeline_pack/agents/llm_normalizer_agent.py`
- **Processors**: Helpers in `src/pipeline_pack/processors/` for normalization, PCID matching, and QC rules.

## Usage
1. Enable the LLM normalization step in pipeline definitions when sources require text cleanup or enrichment.
2. Review agent configuration defaults in `config/agents/defaults.yaml` (or pipeline-pack equivalents) before enabling in production.
3. Track operational status and experiments in this document to keep costs and quality in check.

## Current status
- LLM normalization is available but not enabled by default; validate performance before broad rollout.
