"""
Chile mapping rules.
"""
from __future__ import annotations

from typing import Dict


def to_pcid(record: Dict[str, object]) -> Dict[str, object]:
    record = dict(record)
    sku = record.get("pcid") or record.get("sku") or ""
    record["pcid"] = f"CHILE-{sku}"
    record.setdefault("currency", "CLP")
    return record

