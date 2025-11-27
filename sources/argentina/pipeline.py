"""
Argentina source pipeline wrapper for DSL-based execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from src.entrypoints.run_pipeline import run_pipeline


@dataclass
class ArgentinaPipeline:
    source: str = "argentina"
    default_environment: str = "prod"
    default_run_type: str = "FULL_REFRESH"
    default_params: Dict[str, Any] = field(default_factory=dict)

    def run(
        self,
        run_type: str | None = None,
        environment: str | None = None,
        **params: Any,
    ) -> Dict[str, Any]:
        merged_params = {**self.default_params, **params}
        return run_pipeline(
            source=self.source,
            run_type=run_type or self.default_run_type,
            params=merged_params,
            environment=environment or self.default_environment,
        )


def run(**kwargs: Any) -> Dict[str, Any]:
    """Convenience function for tooling."""
    pipeline = ArgentinaPipeline()
    return pipeline.run(**kwargs)

