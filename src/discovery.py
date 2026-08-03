from __future__ import annotations

import logging
from typing import Dict

from .io_utils import read_json, write_json
from .models import Kayak
from .walmart_client import discover_from_search
from datetime import datetime
import os

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

    # If we discovered nothing and it looks like Walmart blocked us, provide a
    # small sample fallback to enable end-to-end testing (can be disabled by
    # setting SKIP_FALLBACK=1).
    if len(out) == 0 and os.environ.get("SKIP_FALLBACK") != "1":
        try:
            debug_path = "data/debug_search_page_1.html"
            if os.path.exists(debug_path):
                html = open(debug_path, "r", encoding="utf-8").read()
                if "Robot or human" in html or "Robot or human?" in html:
                    logger.warning("Detected Walmart bot challenge; seeding sample catalog for tests")
                    now = datetime.utcnow().isoformat() + "Z"
                    sample = [
                        Kayak(sku="0000001", name="Sample Kayak A", url="https://www.walmart.com/ip/Sample-Kayak-A/0000001", first_seen=now, last_seen=now).to_dict(),
                        Kayak(sku="0000002", name="Sample Kayak B", url="https://www.walmart.com/ip/Sample-Kayak-B/0000002", first_seen=now, last_seen=now).to_dict(),
                    ]
                    write_json("data/kayaks.json", sample)
                    logger.info("Wrote %d sample kayaks to data/kayaks.json", len(sample))
        except Exception:
            logger.exception("Failed to write fallback sample kayaks")
