from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

from .io_utils import read_json


def _days_between(a: str, b: str) -> int:
    da = datetime.fromisoformat(a.replace("Z", ""))
    db = datetime.fromisoformat(b.replace("Z", ""))
    return abs((db - da).days)


def compute_clearance_scores() -> List[Dict[str, Any]]:
    history = read_json("data/history.json", []) or []
    kayaks = {}
    for entry in history:
        sku = entry["sku"]
        kayaks.setdefault(sku, []).append(entry)

    results = []
    for sku, records in kayaks.items():
        # Compute discount percent based on first list_price encountered
        prices = [r.get("price") for r in records if r.get("price") is not None]
        list_prices = [r.get("list_price") for r in records if r.get("list_price")]
        if not prices:
            continue
        current_price = prices[-1]
        list_price = list_prices[0] if list_prices else None
        discount_percent = 0.0
        if list_price and list_price > 0:
            discount_percent = round((list_price - current_price) / list_price * 100, 2)

        # markdown_count: number of times price decreased compared to previous
        markdown_count = 0
        prev_price = None
        first_markdown_ts = None
        for r in records:
            p = r.get("price")
            if prev_price is not None and p is not None and p < prev_price:
                markdown_count += 1
                if first_markdown_ts is None:
                    first_markdown_ts = r.get("timestamp")
            prev_price = p if p is not None else prev_price

        days_since_first_markdown = 0
        if first_markdown_ts:
            days_since_first_markdown = _days_between(first_markdown_ts, records[-1].get("timestamp"))

        clearance_score = discount_percent + (markdown_count * 10) + days_since_first_markdown
        results.append({
            "sku": sku,
            "name": records[-1].get("name"),
            "url": records[-1].get("url"),
            "discount_percent": discount_percent,
            "markdown_count": markdown_count,
            "days_since_first_markdown": days_since_first_markdown,
            "clearance_score": clearance_score,
        })

    # sort descending by clearance_score
    return sorted(results, key=lambda r: r["clearance_score"], reverse=True)
