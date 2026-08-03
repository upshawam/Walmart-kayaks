from __future__ import annotations

import logging
from typing import Dict, List

from .io_utils import read_json, write_json
from .models import ChangeEvent

logger = logging.getLogger(__name__)


def detect_changes() -> List[Dict]:
    latest = read_json("data/latest.json", []) or []
    prev_latest = read_json("data/.prev_latest.json", []) or []
    changes = read_json("data/changes.json", []) or []

    # Build map keyed by sku+store
    prev_map = {f"{r['sku']}|{r['store']}": r for r in prev_latest}

    events = []
    for r in latest:
        key = f"{r['sku']}|{r['store']}"
        prev = prev_map.get(key)
        if not prev:
            e = ChangeEvent(sku=r['sku'], name=r.get('name',''), url=r.get('url',''), store=r['store'], event='new_snapshot', old=None, new=r)
            events.append(e.to_dict())
            continue
        # price change
        old_price = prev.get('price')
        new_price = r.get('price')
        if old_price is not None and new_price is not None and new_price != old_price:
            ev = 'price_drop' if new_price < old_price else 'price_increase'
            e = ChangeEvent(sku=r['sku'], name=r.get('name',''), url=r.get('url',''), store=r['store'], event=ev, old=old_price, new=new_price)
            events.append(e.to_dict())
        # stock flip
        old_stock = prev.get('in_stock')
        new_stock = r.get('in_stock')
        if old_stock is not None and new_stock is not None and old_stock != new_stock:
            e = ChangeEvent(sku=r['sku'], name=r.get('name',''), url=r.get('url',''), store=r['store'], event='stock_flip', old=old_stock, new=new_stock)
            events.append(e.to_dict())

    if events:
        changes.extend(events)
        write_json("data/changes.json", changes)
    # persist prev latest for next run
    write_json("data/.prev_latest.json", latest)
    logger.info("Detected %d events", len(events))
    return events
