from __future__ import annotations

import logging
import re
import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from playwright.sync_api import sync_playwright

from .config import SETTINGS

logger = logging.getLogger(__name__)


def _extract_sku_from_url(url: str) -> Optional[str]:
    m = re.search(r"/ip/(?:.+?)/([0-9]+)", url)
    if m:
        return m.group(1)
    m2 = re.search(r"/product/([0-9]+)", url)
    if m2:
        return m2.group(1)
    return None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10), retry=retry_if_exception_type(Exception))
def fetch_page(url: str) -> str:
    logger.info("Fetching page %s", url)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=SETTINGS.playwright_headless)
        try:
            page = browser.new_page(user_agent=SETTINGS.user_agent)
            page.goto(url, timeout=30000)
            time.sleep(0.8)
            content = page.content()
            return content
        finally:
            browser.close()


def discover_from_search(pages: int = 3) -> List[Dict]:
    """Search Walmart for 'kayak' and yield discovered products.

    This is a resilient HTML-based discovery. It prefers structured data if present.
    """
    found = {}
    for p in range(1, pages + 1):
        url = f"https://www.walmart.com/search/?query=kayak&page={p}"
        try:
            html = fetch_page(url)
        except Exception:
            logger.exception("Failed to fetch search page %s", url)
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a.product-title-link, a.search-result-product-title-link"):
            href = a.get("href")
            if not href:
                continue
            if href.startswith("/"):
                href = "https://www.walmart.com" + href
            sku = _extract_sku_from_url(href) or a.get("data-item-id")
            name = a.get_text(strip=True) or a.get("aria-label") or ""
            if not sku:
                # try to extract from data-analytics
                pass
            if not sku:
                continue
            found[sku] = {"sku": sku, "name": name, "url": href}
        time.sleep(SETTINGS.rate_limit_seconds)
    return list(found.values())


def parse_product_page(html: str) -> Dict:
    """Attempt to parse price and availability from a Walmart product page.

    Return dict with keys: price, list_price, in_stock
    """
    soup = BeautifulSoup(html, "html.parser")
    # Try JSON-LD first
    script = soup.find_all("script", type="application/ld+json")
    for s in script:
        try:
            import json

            data = json.loads(s.string)
            if isinstance(data, dict) and data.get("@type") in ("Product",):
                offers = data.get("offers") or {}
                price = offers.get("price")
                list_price = offers.get("priceSpecification", {}).get("price") if isinstance(offers.get("priceSpecification"), dict) else None
                availability = offers.get("availability")
                in_stock = None
                if availability:
                    in_stock = "InStock" in availability
                return {"price": float(price) if price else None, "list_price": float(list_price) if list_price else None, "in_stock": in_stock}
        except Exception:
            continue

    # Fallback: look for price class
    price_text = None
    el = soup.select_one("span.price-characteristic") or soup.select_one("span[itemprop='price']")
    if el:
        price_text = el.get("content") or el.get_text()
    if not price_text:
        # find any dollar amounts
        m = re.search(r"\$\s*([0-9,.]+)", soup.get_text())
        if m:
            price_text = m.group(1)
    price = None
    if price_text:
        try:
            price = float(str(price_text).replace("$", "").replace(",", ""))
        except Exception:
            price = None

    in_stock = True
    if soup.find(string=re.compile(r"out of stock", re.I)):
        in_stock = False

    return {"price": price, "list_price": None, "in_stock": in_stock}


def get_product_snapshot(url: str) -> Dict:
    try:
        html = fetch_page(url)
        info = parse_product_page(html)
        return info
    except Exception:
        logger.exception("Failed to get product snapshot for %s", url)
        return {"price": None, "list_price": None, "in_stock": None}
