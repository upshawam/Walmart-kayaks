from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


def ts_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Kayak:
    sku: str
    name: str
    url: str
    first_seen: str = field(default_factory=ts_now)
    last_seen: str = field(default_factory=ts_now)
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Snapshot:
    sku: str
    name: str
    url: str
    store: str
    price: Optional[float]
    list_price: Optional[float]
    in_stock: Optional[bool]
    timestamp: str = field(default_factory=ts_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChangeEvent:
    sku: str
    name: str
    url: str
    store: str
    event: str
    old: Any = None
    new: Any = None
    timestamp: str = field(default_factory=ts_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
