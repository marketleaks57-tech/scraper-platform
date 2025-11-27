"""
LLM DSL Compiler - Convert natural language to DSL pipelines.

This module provides functionality to convert natural language descriptions
into executable DSL pipeline definitions.

Example:
    "Run Alfabeta full crawl, only for OTC category, last 6 months changes"
    -> DSL pipeline YAML with filters and date ranges
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.logging_utils import get_logger
from src.processors.llm.llm_client import LLMClient, get_llm_client_from_config

log = get_logger("llm-dsl-compiler")


def compile_natural_language_to_dsl(
    description: str,
    source_config: Optional[Dict[str, Any]] = None,
    llm_client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """
    Convert natural language description to DSL pipeline.
    
    Args:
        description: Natural language description of the pipeline
        source_config: Optional source configuration for context
        llm_client: Optional LLM client (will be created from config if not provided)
    
    Returns:
        DSL pipeline definition as dict
    
    Example:
        >>> compile_natural_language_to_dsl(
        ...     "Run Alfabeta full crawl, only for OTC category, last 6 months changes"
        ... )
        {
            "pipeline": {
                "name": "alfabeta_otc_6months",
                "description": "...",
                "steps": [...]
            }
        }
    """
    if llm_client is None:
        if source_config:
            llm_client = get_llm_client_from_config(source_config.get("llm", {}))
        else:
            raise ValueError("Either llm_client or source_config with LLM config must be provided")
    
    if llm_client is None:
        raise ValueError("LLM client not available. Configure LLM in source config.")
    
    system_prompt = """You are a DSL compiler that converts natural language descriptions into executable pipeline definitions.

The DSL format is YAML with this structure:
```yaml
pipeline:
  name: <pipeline_name>
  description: <description>
  steps:
    - id: <step_id>
      component: <component_name>
      params:
        <param_name>: <param_value>
```

Common components:
- {source}.pipeline - Full pipeline execution
- filters.category - Filter by category
- filters.date_range - Filter by date range
- filters.source - Filter by source

Extract:
- Source name (e.g., "Alfabeta", "Quebec")
- Categories (e.g., "OTC", "prescription")
- Date ranges (e.g., "last 6 months", "since 2024-01-01")
- Filters and constraints

Return valid YAML as JSON."""
    
    user_prompt = f"""Convert this natural language description to a DSL pipeline:

{description}

Provide the pipeline definition as JSON (YAML structure as JSON object)."""
    
    try:
        result = llm_client.extract_json(system_prompt, user_prompt)
        
        # Validate and structure the result
        if isinstance(result, dict):
            # Ensure it has the pipeline structure
            if "pipeline" not in result:
                result = {"pipeline": result}
            
            # Add default steps if missing
            if "steps" not in result.get("pipeline", {}):
                source_name = _extract_source_name(description)
                result["pipeline"]["steps"] = [
                    {
                        "id": "run_pipeline",
                        "component": f"{source_name}.pipeline",
                        "params": {},
                    }
                ]
            
            return result
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")
    
    except Exception as exc:
        log.error("Failed to compile natural language to DSL", extra={"error": str(exc)})
        raise ValueError(f"DSL compilation failed: {exc}") from exc


def _extract_source_name(description: str) -> str:
    """Extract source name from description (fallback)."""
    description_lower = description.lower()
    sources = ["alfabeta", "quebec", "lafa", "chile", "argentina"]
    for source in sources:
        if source in description_lower:
            return source
    return "template"


def save_dsl_pipeline(pipeline: Dict[str, Any], output_path: Path) -> None:
    """Save DSL pipeline to YAML file."""
    import yaml
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(pipeline, f, default_flow_style=False, sort_keys=False)
    
    log.info("Saved DSL pipeline", extra={"path": str(output_path)})

