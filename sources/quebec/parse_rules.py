"""
Quebec parser rules.
"""
from __future__ import annotations

from typing import Any, Dict


def parse_listing_node(node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pcid": node.get("sku") or node.get("id"),
        "product_name": node.get("name"),
        "price": _normalize_price(node.get("price")),
        "currency": node.get("currency", "CAD"),
        "availability": node.get("availability", "unknown"),
        "province": "QC",
    }


def _normalize_price(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if not value:
        return 0.0
    cleaned = value.replace("$", "").replace("CAD", "").replace(",", ".").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

