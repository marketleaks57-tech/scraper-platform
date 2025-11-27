"""
Argentina-specific parsing helpers used by DSL parse nodes.
"""
from __future__ import annotations

from typing import Any, Dict


def normalize_price(value: str | float | int) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = (
        value.replace("$", "")
        .replace("ARS", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_listing_node(node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pcid": node.get("sku") or node.get("id"),
        "product_name": node.get("name"),
        "price": normalize_price(node.get("price", 0)),
        "currency": node.get("currency", "ARS"),
        "url": node.get("url"),
        "availability": node.get("availability", "unknown"),
    }

