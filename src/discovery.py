from __future__ import annotations

import logging
from typing import Dict

from .io_utils import read_json, write_json
from .models import Kayak
from .walmart_client import discover_from_search

logger = logging.getLogger(__name__)


def run_discovery(pages: int = None) -> None:
    pages = pages or 3
    existing = read_json("data/kayaks.json", []) or []
    existing_map: Dict[str, Dict] = {k["sku"]: k for k in existing}
    discovered = discover_from_search(pages)

    for d in discovered:
        sku = d["sku"]
        if sku in existing_map:
            existing_map[sku]["last_seen"] = d.get("last_seen") or existing_map[sku].get("last_seen")
            existing_map[sku]["active"] = True
            existing_map[sku]["name"] = d.get("name") or existing_map[sku].get("name")
            existing_map[sku]["url"] = d.get("url") or existing_map[sku].get("url")
        else:
            k = Kayak(sku=sku, name=d.get("name", ""), url=d.get("url", ""))
            existing_map[sku] = k.to_dict()

    # mark missing as inactive
    discovered_skus = {d["sku"] for d in discovered}
    for sku, obj in existing_map.items():
        if sku not in discovered_skus:
            obj["active"] = False

    out = list(existing_map.values())
    write_json("data/kayaks.json", out)
    logger.info("Discovery complete: %d kayaks saved", len(out))
