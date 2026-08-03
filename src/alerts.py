from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import List

from .io_utils import read_json

logger = logging.getLogger(__name__)


def send_alerts(events: List[dict]) -> None:
    if not events:
        return
    server = None
    try:
        SMTP_SERVER = __import__("os").environ.get("SMTP_SERVER")
        SMTP_PORT = int(__import__("os").environ.get("SMTP_PORT", "587"))
        SMTP_USERNAME = __import__("os").environ.get("SMTP_USERNAME")
        SMTP_PASSWORD = __import__("os").environ.get("SMTP_PASSWORD")
        EMAIL_FROM = __import__("os").environ.get("EMAIL_FROM")
        EMAIL_TO = __import__("os").environ.get("EMAIL_TO")

        if not SMTP_SERVER or not EMAIL_TO:
            logger.warning("SMTP_SERVER or EMAIL_TO not set; skipping alerts")
            return

        msg = EmailMessage()
        msg["Subject"] = f"Walmart Kayak Monitor: {len(events)} changes detected"
        msg["From"] = EMAIL_FROM or SMTP_USERNAME
        msg["To"] = EMAIL_TO
        body_lines = [f"Detected {len(events)} change events:\n"]
        for e in events:
            body_lines.append(f"- {e.get('event')} {e.get('sku')} @ {e.get('store')}: {e.get('old')} -> {e.get('new')}")
        msg.set_content("\n".join(body_lines))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        logger.info("Alert email sent to %s", EMAIL_TO)
    except Exception:
        logger.exception("Failed to send alert email")
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
