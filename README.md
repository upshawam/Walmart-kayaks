# Walmart Kayaks Tracker

Purpose: discover and monitor Walmart kayaks for price and stock changes near ZIP `37066` and generate a static dashboard.

Quick start

- Add repository secrets (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`).
- Enable GitHub Pages for branch `main` and folder `/docs`.
- Workflows: `.github/workflows/weekly-discovery.yml` and `.github/workflows/daily.yml` will run discovery and monitor jobs.

Local run

Install requirements and Playwright browsers:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Run discovery:

```bash
python -m src.main discover
```

Run monitor (daily):

```bash
python -m src.main monitor
```

Files

- `data/kayaks.json`: discovered kayak catalog
- `data/latest.json`: last run snapshots
- `data/history.json`: append-only history
- `data/changes.json`: change events
- `docs/dashboard-data.json`: generated dashboard JSON consumed by `docs/index.html`

Workflows

- `daily.yml`: runs daily and on workflow_dispatch; runs monitor -> detect -> alerts -> dashboard -> commit
- `weekly-discovery.yml`: runs weekly to discover new products and update `data/kayaks.json`

Notes & troubleshooting

- This project prefers structured data on Walmart product pages; if the site changes, you may need to update `src/walmart_client.py` parsing logic.
- Be mindful of Walmart anti-bot protections. Playwright uses a real browser; if CI runs are blocked, consider adding delays or rotating IPs.
