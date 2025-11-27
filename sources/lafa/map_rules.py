"""
LAFA mapping helpers.
"""
from __future__ import annotations

from typing import Dict


def to_pcid(record: Dict[str, object]) -> Dict[str, object]:
    record = dict(record)
    sku = (record.get("pcid") or record.get("sku") or "")[:20]
    record["pcid"] = f"LAFA-{sku}"
    record.setdefault("currency", "BRL")
    return record

