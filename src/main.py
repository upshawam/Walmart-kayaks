from __future__ import annotations

import argparse
import logging
import sys

from . import discovery, monitor, changes, dashboard, alerts

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("walmart_kayaks")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="walmart-kayaks")
    parser.add_argument("action", choices=["discover", "monitor", "full"], help="Action to run")
    args = parser.parse_args(argv)

    if args.action == "discover":
        discovery.run_discovery()
        return 0

    if args.action == "monitor":
        monitor.run_monitor()
        events = changes.detect_changes()
        if events:
            alerts.send_alerts(events)
        dashboard.build_dashboard_assets()
        return 0

    if args.action == "full":
        discovery.run_discovery()
        monitor.run_monitor()
        events = changes.detect_changes()
        if events:
            alerts.send_alerts(events)
        dashboard.build_dashboard_assets()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
