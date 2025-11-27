import sys
import threading
import time
from pathlib import Path

import pytest

from src.core_kernel import ComponentRegistry, ExecutionEngine, PipelineCompiler
from src.core_kernel.pipeline_compiler import CompiledPipeline, CompiledStep


DSL_ROOT = Path(__file__).resolve().parent.parent / "dsl"


def test_registry_loads_components():
    registry = ComponentRegistry.from_yaml(DSL_ROOT / "components.yaml")
    alfabeta_pipeline = registry.get("alfabeta.pipeline")

    assert alfabeta_pipeline is not None
    assert alfabeta_pipeline.module == "src.scrapers.alfabeta.pipeline"
    callable_obj = registry.resolve_callable("alfabeta.pipeline")
    assert callable(callable_obj)


def test_pipeline_compiles_against_registry():
    registry = ComponentRegistry.from_yaml(DSL_ROOT / "components.yaml")
    compiler = PipelineCompiler(registry)
    compiled = compiler.compile_from_file(DSL_ROOT / "pipelines" / "alfabeta.yaml")

    assert compiled.name == "alfabeta"
    assert compiled.steps[0].component.name == "alfabeta.pipeline"
    assert [v.id for v in compiled.variants] == ["v1_baseline", "v2_aggressive_pcids"]


def test_execution_engine_runs_pipeline(monkeypatch):
    registry = ComponentRegistry.from_yaml(DSL_ROOT / "components.yaml")
    compiler = PipelineCompiler(registry)
    compiled = compiler.compile_from_file(DSL_ROOT / "pipelines" / "alfabeta.yaml")

    called = {}

    def fake_run_alfabeta(env=None):
        called["env"] = env
        return "ok"

    import src.scrapers.alfabeta.pipeline as pipeline

    monkeypatch.setattr(pipeline, "run_alfabeta", fake_run_alfabeta)

    engine = ExecutionEngine(registry)
    results = engine.execute(compiled, runtime_params={"env": "unit"})

    assert results["run_pipeline"] == "ok"
    assert called["env"] == "unit"


def test_execution_engine_honors_dependencies_and_runs_ready_steps_in_parallel():
    registry = ComponentRegistry()
    execution_order = []

    def step_a():
        execution_order.append("step_a")
        return "A"

    def step_b():
        execution_order.append("step_b")
        return "B"

    def step_c():
        execution_order.append("step_c")
        return "C"

    current_module = sys.modules[__name__]
    setattr(current_module, "step_a", step_a)
    setattr(current_module, "step_b", step_b)
    setattr(current_module, "step_c", step_c)

    registry.register("step_a", __name__, "step_a", type="fetch")
    registry.register("step_b", __name__, "step_b", type="parse")
    registry.register("step_c", __name__, "step_c", type="parse")

    pipeline = CompiledPipeline(
        name="parallel",
        description="",
        steps=[
            CompiledStep(
                id="step_a",
                component=registry.get("step_a"),
                params={},
                depends_on=[],
                step_type="fetch",
            ),
            CompiledStep(
                id="step_b",
                component=registry.get("step_b"),
                params={},
                depends_on=["step_a"],
                step_type="parse",
            ),
            CompiledStep(
                id="step_c",
                component=registry.get("step_c"),
                params={},
                depends_on=["step_a"],
                step_type="parse",
            ),
        ],
        variants=[],
    )

    engine = ExecutionEngine(registry)
    results = engine.execute(pipeline)

    assert execution_order[0] == "step_a"
    assert set(execution_order[1:]) == {"step_b", "step_c"}
    assert results == {"step_a": "A", "step_b": "B", "step_c": "C"}


def test_side_effecting_steps_run_deterministically():
    registry = ComponentRegistry()
    export_one_finished = threading.Event()

    def export_one():
        time.sleep(0.05)
        export_one_finished.set()
        return "first"

    def export_two():
        assert export_one_finished.is_set(), "side-effecting steps should run in order"
        return "second"

    current_module = sys.modules[__name__]
    setattr(current_module, "export_one", export_one)
    setattr(current_module, "export_two", export_two)

    registry.register("export_one", __name__, "export_one", type="export")
    registry.register("export_two", __name__, "export_two", type="export")

    pipeline = CompiledPipeline(
        name="exports",
        description="",
        steps=[
            CompiledStep(
                id="export_one",
                component=registry.get("export_one"),
                params={},
                depends_on=[],
                step_type="export",
            ),
            CompiledStep(
                id="export_two",
                component=registry.get("export_two"),
                params={},
                depends_on=[],
                step_type="export",
            ),
        ],
        variants=[],
    )

    engine = ExecutionEngine(registry)
    results = engine.execute(pipeline)

    assert export_one_finished.is_set()
    assert results == {"export_one": "first", "export_two": "second"}


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
