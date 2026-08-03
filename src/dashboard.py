from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

from .io_utils import read_json, write_json
from .scoring import compute_clearance_scores

logger = logging.getLogger(__name__)


def build_dashboard_assets() -> None:
    latest = read_json("data/latest.json", []) or []
    changes = read_json("data/changes.json", []) or []
    clearance = compute_clearance_scores()

    data = {
        "latest": latest,
        "changes": changes[-200:],
        "clearance": clearance[:100],
    }

    write_json("docs/dashboard-data.json", data)

    # write minimal index.html and assets if missing
    docs = Path.cwd().joinpath("docs")
    docs.mkdir(parents=True, exist_ok=True)
    # styles and app are assumed present; ensure they exist as placeholders if not
    if not docs.joinpath("index.html").exists():
        docs.joinpath("index.html").write_text("""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\"><title>Walmart Kayaks Dashboard</title>
  <link rel=\"stylesheet\" href=\"styles.css\"> 
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <script defer src=\"app.js\"></script>
</head>
<body>
  <h1>Walmart Kayaks Dashboard</h1>
  <div id=\"app\">Loading...</div>
</body>
</html>""", encoding="utf-8")
    if not docs.joinpath("styles.css").exists():
        docs.joinpath("styles.css").write_text("body{font-family:Arial,sans-serif;margin:20px}")
    if not docs.joinpath("app.js").exists():
        docs.joinpath("app.js").write_text("""async function init(){const r=await fetch('dashboard-data.json');const d=await r.json();document.getElementById('app').innerText=JSON.stringify({counts:{latest:d.latest.length,changes:d.changes.length,clearance:d.clearance.length}},null,2);}init();""")

    logger.info("Dashboard assets written to docs/")
