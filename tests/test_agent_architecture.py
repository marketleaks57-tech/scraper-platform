from __future__ import annotations

from typing import Any

import pytest

from src.agents.base import AgentConfig, AgentContext, BaseAgent
from src.agents.orchestrator import AgentOrchestrator
from src.agents.registry import AgentRegistry


class DummyAgent(BaseAgent):
    def __init__(self, name: str, *, value: Any = None, score: int = 0):
        super().__init__(name=name, config=AgentConfig())
        self.value = value
        self.score = score

    def run(self, context: AgentContext) -> AgentContext:
        if self.value is not None:
            context[self.name] = self.value
        context["quality_score"] = self.score
        return context


def test_agent_context_nested_access_and_merge():
    ctx = AgentContext({"a": {"b": 1}})
    assert ctx.get_nested("a.b") == 1

    ctx.set_nested("a.c", 2)
    assert ctx.get_nested("a.c") == 2

    ctx.merge({"d": 4})
    assert ctx["d"] == 4


def test_registry_registers_and_returns_fresh_instances():
    registry = AgentRegistry()
    registry.register_factory("agent1", lambda: DummyAgent("agent1", value=1))

    first = registry.get("agent1")
    second = registry.get("agent1")

    assert first is not second
    assert first.name == "agent1"
    assert registry.list_agents()["agent1"].name == "agent1"


def test_orchestrator_runs_simple_pipeline():
    registry = AgentRegistry()
    registry.register_factory("step1", lambda: DummyAgent("step1", value="done"))

    pipelines = {"sources": {"demo": {"pipeline": [{"agent": "step1"}]}}}
    orchestrator = AgentOrchestrator(registry, pipelines)
    ctx = AgentContext()

    result = orchestrator.run_pipeline("demo", ctx)
    assert result.get("step1") == "done"


def test_orchestrator_parallel_block_merges_results():
    registry = AgentRegistry()
    registry.register_factory("a", lambda: DummyAgent("a", value=1))
    registry.register_factory("b", lambda: DummyAgent("b", value=2))

    pipelines = {
        "sources": {
            "demo": {
                "pipeline": [
                    {"parallel": [{"agent": "a"}, {"agent": "b"}]},
                ]
            }
        }
    }
    orchestrator = AgentOrchestrator(registry, pipelines)
    ctx = AgentContext()

    result = orchestrator.run_pipeline("demo", ctx)
    assert result["a"] == 1
    assert result["b"] == 2
    assert "parallel_results" in result.metadata


def test_orchestrator_ensemble_picks_best_score():
    registry = AgentRegistry()
    registry.register_factory("low", lambda: DummyAgent("low", value="low", score=1))
    registry.register_factory("high", lambda: DummyAgent("high", value="high", score=10))

    pipelines = {
        "sources": {
            "demo": {
                "pipeline": [
                    {
                        "ensemble": {
                            "strategy": "best_score",
                            "agents": [
                                {"agent": "low"},
                                {"agent": "high"},
                            ],
                        }
                    }
                ]
            }
        }
    }
    orchestrator = AgentOrchestrator(registry, pipelines)
    ctx = AgentContext()

    result = orchestrator.run_pipeline("demo", ctx)
    assert result.get("high") == "high"
    assert result.get("quality_score") == 10


def test_orchestrator_ensemble_first_success_returns_early():
    registry = AgentRegistry()
    registry.register_factory("first", lambda: DummyAgent("first", value="a", score=1))
    registry.register_factory("second", lambda: DummyAgent("second", value="b", score=100))

    pipelines = {
        "sources": {
            "demo": {
                "pipeline": [
                    {
                        "ensemble": {
                            "strategy": "first_success",
                            "agents": [
                                {"agent": "first"},
                                {"agent": "second"},
                            ],
                        }
                    }
                ]
            }
        }
    }
    orchestrator = AgentOrchestrator(registry, pipelines)
    ctx = AgentContext()

    result = orchestrator.run_pipeline("demo", ctx)
    assert result.get("first") == "a"
    assert "second" not in result
