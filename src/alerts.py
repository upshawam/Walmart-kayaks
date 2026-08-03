from __future__ import annotations

import logging
import os
from typing import List

import requests

logger = logging.getLogger(__name__)


def send_alerts(events: List[dict]) -> None:
    """Create a GitHub Issue summarizing change events.

    Requires `GITHUB_REPOSITORY` (owner/repo) and `GITHUB_TOKEN` in the environment.
    When running in GitHub Actions these are provided automatically.
    """
    if not events:
        return

    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        logger.warning("GITHUB_REPOSITORY or GITHUB_TOKEN not set; skipping GitHub Issue creation")
        return

    owner_repo = repo.split("/")
    if len(owner_repo) != 2:
        logger.error("Invalid GITHUB_REPOSITORY value: %s", repo)
        return
    owner, repo_name = owner_repo
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"

    title = f"Walmart Kayaks Monitor: {len(events)} change(s) detected"
    body_lines = [f"Detected {len(events)} change events:", ""]
    for e in events:
        body_lines.append(f"- {e.get('event')} — {e.get('sku')} @ {e.get('store')}: {e.get('old')} -> {e.get('new')}")

    payload = {
        "title": title,
        "body": "\n".join(body_lines),
        "labels": ["walmart-monitor"],
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "walmart-kayaks-agent",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code in (200, 201):
            logger.info("Created GitHub issue for %d events", len(events))
        else:
            logger.error("Failed to create issue: %s %s", resp.status_code, resp.text)
    except Exception:
        logger.exception("Exception while creating GitHub issue for events")

