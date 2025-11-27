"""
Argentina mapping rules to harmonize parsed records.
"""
from __future__ import annotations

from typing import Dict


def to_pcid(record: Dict[str, object]) -> Dict[str, object]:
    record = dict(record)
    sku = record.get("pcid") or record.get("sku")
    record["pcid"] = f"ARG-{sku}" if sku else None
    record.setdefault("currency", "ARS")
    return record

