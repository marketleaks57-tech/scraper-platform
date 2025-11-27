"""Simple load/stress test harness for scraper pipelines.

This tool executes a configured DSL pipeline many times with configurable
concurrency, proxy/account pools, and captures runtime statistics. It is meant
for exercising resource manager behavior and producing baseline performance
metrics.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import math
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from src.common.logging_utils import get_logger
from src.core_kernel import CompiledPipeline, ComponentRegistry, ExecutionEngine, PipelineCompiler
from src.observability.run_trace_context import get_current_run_id
from src.scheduler import scheduler_db_adapter

log = get_logger("load-test")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PIPELINE_NAME = "alfabeta"


@dataclass
class RunResult:
    run_number: int
    run_id: Optional[str]
    success: bool
    duration_seconds: float
    records_written: Optional[int] = None
    error: Optional[str] = None


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(math.ceil(pct / 100 * len(ordered)) - 1, 0)
    return ordered[rank]


def _configure_resources(source: str, proxies: Optional[str], accounts: List[str]) -> None:
    source_upper = source.upper()
    if proxies:
        os.environ[f"{source_upper}_PROXIES"] = proxies
        log.info("Configured proxies for %s", source)

    for idx, account in enumerate(accounts, start=1):
        if ":" not in account:
            raise ValueError("Accounts must be provided as username:password")
        username, password = account.split(":", 1)
        os.environ[f"{source_upper}_USER_{idx}"] = username
        os.environ[f"{source_upper}_PASS_{idx}"] = password
    if accounts:
        log.info("Configured %d accounts for %s", len(accounts), source)


def _load_compiled_pipeline(pipeline_name: str) -> tuple[ExecutionEngine, CompiledPipeline]:
    registry_path = REPO_ROOT / "dsl" / "components.yaml"
    pipeline_path = REPO_ROOT / "dsl" / "pipelines" / f"{pipeline_name}.yaml"

    registry = ComponentRegistry.from_yaml(registry_path)
    compiler = PipelineCompiler(registry)
    compiled = compiler.compile_from_file(pipeline_path)
    engine = ExecutionEngine(registry)
    return engine, compiled


def _fetch_db_rows(run_id: Optional[str]) -> Optional[int]:
    if not run_id:
        return None
    detail = scheduler_db_adapter.fetch_run_detail(run_id)
    if not detail or not detail.stats:
        return None
    stats = detail.stats or {}
    records = stats.get("records")
    return int(records) if isinstance(records, int) else None


def _execute_run(
    run_number: int,
    engine: ExecutionEngine,
    compiled_pipeline: CompiledPipeline,
    runtime_params: Optional[dict[str, object]] = None,
) -> RunResult:
    start = time.perf_counter()
    run_id: Optional[str] = None
    try:
        engine.execute(compiled_pipeline, runtime_params=runtime_params)
        duration = time.perf_counter() - start
        run_id = get_current_run_id()
        records = _fetch_db_rows(run_id)
        return RunResult(run_number, run_id, True, duration, records_written=records)
    except Exception as exc:  # pragma: no cover - runtime guard
        duration = time.perf_counter() - start
        run_id = run_id or get_current_run_id()
        log.exception("Run %s failed", run_number)
        return RunResult(run_number, run_id, False, duration, error=str(exc))


def _print_summary(results: Iterable[RunResult]) -> None:
    results = list(results)
    total = len(results)
    successes = sum(1 for r in results if r.success)
    failures = total - successes
    durations = [r.duration_seconds for r in results]

    avg = statistics.mean(durations) if durations else 0.0
    p95 = _percentile(durations, 95)

    log.info("Load test complete: %d runs (%d success / %d failure)", total, successes, failures)
    log.info("Average runtime: %.2fs | P95 runtime: %.2fs", avg, p95)

    for res in results:
        status = "ok" if res.success else "failed"
        msg = f"Run {res.run_number}: {status} in {res.duration_seconds:.2f}s"
        if res.records_written is not None:
            msg += f" | rows={res.records_written}"
        if res.run_id:
            msg += f" | run_id={res.run_id}"
        if res.error:
            msg += f" | error={res.error}"
        log.info(msg)


def run_load_test(
    runs: int,
    concurrency: int,
    pipeline: str,
    runtime_params: Optional[dict[str, object]],
    proxies: Optional[str],
    accounts: List[str],
) -> List[RunResult]:
    _configure_resources(pipeline, proxies, accounts)
    engine, compiled_pipeline = _load_compiled_pipeline(pipeline)
    results: List[RunResult] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_map = {
            executor.submit(_execute_run, idx + 1, engine, compiled_pipeline, runtime_params): idx + 1
            for idx in range(runs)
        }
        for future in concurrent.futures.as_completed(future_map):
            results.append(future.result())

    _print_summary(results)
    return results


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run load tests against a DSL pipeline")
    parser.add_argument("--runs", type=int, default=5, help="Total number of pipeline runs to execute")
    parser.add_argument("--concurrency", type=int, default=2, help="Number of concurrent worker threads")
    parser.add_argument("--pipeline", default=DEFAULT_PIPELINE_NAME, help="Pipeline name (matches DSL filename)")
    parser.add_argument("--env", default=None, help="Optional runtime env passed into the pipeline")
    parser.add_argument("--variant", default=None, help="Optional variant id for A/B experiments")
    parser.add_argument(
        "--proxies",
        default=None,
        help="Comma-separated proxy list applied via <SOURCE>_PROXIES for resource manager",
    )
    parser.add_argument(
        "--account",
        action="append",
        default=[],
        help="Add an account credential in username:password form (repeat for multiple)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":  # pragma: no cover
    args = parse_args()
    runtime_params = {}
    if args.env is not None:
        runtime_params["env"] = args.env
    if args.variant is not None:
        runtime_params["variant_id"] = args.variant
    if not runtime_params:
        runtime_params = None
    run_load_test(
        runs=args.runs,
        concurrency=args.concurrency,
        pipeline=args.pipeline,
        runtime_params=runtime_params,
        proxies=args.proxies,
        accounts=args.account,
    )
