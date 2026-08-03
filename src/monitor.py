from __future__ import annotations

import logging
from typing import List

from .io_utils import read_json, write_json
from .models import Snapshot
from .walmart_client import get_product_snapshot
from .config import SETTINGS
import os
import random
from datetime import datetime

logger = logging.getLogger(__name__)


def run_monitor() -> None:
    kayaks = read_json("data/kayaks.json", []) or []
    latest: List[dict] = []
    history = read_json("data/history.json", []) or []

    for k in kayaks:
        sku = k.get("sku")
        name = k.get("name")
        url = k.get("url")
        # For each configured store, perform a best-effort snapshot
        for store in SETTINGS.stores:
            if os.environ.get("DRY_RUN") == "1":
                # generate fake snapshot data for testing
                price = round(random.uniform(199.0, 899.0), 2)
                list_price = round(price + random.uniform(20.0, 200.0), 2)
                in_stock = random.choice([True, True, False])
                info = {"price": price, "list_price": list_price, "in_stock": in_stock}
                timestamp = datetime.utcnow().isoformat() + "Z"
            else:
                info = get_product_snapshot(url)
            s = Snapshot(
                sku=sku,
                name=name,
                url=url,
                store=store,
                price=info.get("price"),
                list_price=info.get("list_price"),
                in_stock=info.get("in_stock"),
            )
            latest.append(s.to_dict())
            history.append(s.to_dict())
    write_json("data/latest.json", latest)
    write_json("data/history.json", history)
    logger.info("Monitor complete: snapshots=%d", len(latest))
