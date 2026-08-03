from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any

_lock = Lock()
_base = Path.cwd()


def _path(rel: str) -> Path:
    p = _base.joinpath(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def read_json(rel: str, default: Any = None) -> Any:
    p = _path(rel)
    with _lock:
        if not p.exists():
            return default
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            logging.exception("Failed to read json %s: %s", rel, e)
            return default


def write_json(rel: str, data: Any) -> None:
    p = _path(rel)
    with _lock:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
