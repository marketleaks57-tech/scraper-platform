"""
High-level QC entrypoints.

Pipelines should import from here, not from individual modules, e.g.:

    from src.processors.qc import run_qc_batch, dedupe_records
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .rules import (
    QCRule,
    QCRuleResult,
    get_default_ruleset,
    run_qc_for_record,
    run_qc_batch as _run_qc_batch,
)
from .dedupe import dedupe_records as _dedupe_records, DuplicateInfo


Record = Dict[str, Any]


__all__ = [
    "QCRule",
    "QCRuleResult",
    "DuplicateInfo",
    "get_default_ruleset",
    "run_qc_for_record",
    "run_qc_batch",
    "dedupe_records",
]


def run_qc_batch(
    records: Iterable[Record],
    *,
    source: Optional[str] = None,
    rules: Optional[Sequence[QCRule]] = None,
) -> Tuple[List[Record], List[Record], List[List[QCRuleResult]]]:
    """
    Public batch QC function.

    Thin wrapper around rules.run_qc_batch to give a stable import path.
    """
    return _run_qc_batch(records, rules=rules, source=source)


def dedupe_records(
    records: Iterable[Record],
    key_fields: Sequence[str],
) -> Tuple[List[Record], List[DuplicateInfo]]:
    """
    Public dedupe function.

    Thin wrapper around qc.dedupe.dedupe_records.
    """
    return _dedupe_records(records, key_fields)
