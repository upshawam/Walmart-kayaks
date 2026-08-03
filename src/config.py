from __future__ import annotations

from dataclasses import dataclass
from typing import List
import os


@dataclass(frozen=True)
class Settings:
    zip_code: str = os.getenv("TARGET_ZIP", "37066")
    stores: List[str] = (
        "Gallatin",
        "Hendersonville",
        "Lebanon",
        "Madison",
        "Mt. Juliet",
        "Hermitage",
    )
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    )
    discovery_pages: int = int(os.getenv("DISCOVERY_PAGES", "5"))
    rate_limit_seconds: float = float(os.getenv("RATE_LIMIT_SECONDS", "1.0"))
    playwright_headless: bool = os.getenv("PLAYWRIGHT_HEADLESS", "1") != "0"


SETTINGS = Settings()
