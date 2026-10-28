"""Read-only source check; prints counts, published date bounds, and status only."""
import argparse
import os
import sys
from datetime import date
from pathlib import Path

# Allow invocation by absolute filename from the dispatcher's native checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.collect.fetchers import get_fetcher
from src.collect.fetchers.congress_gov import _keyring_api_key
from src.collect.runner import load_config, report_window


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-month", required=True,
        help="Issue month in YYYY-MM form; checks the previous calendar month",
    )
    parser.add_argument("--all", action="store_true", help="Check every enabled source in config order")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = load_config(str(root / "src/collect/config.yaml"))["sources"]
    start, end = report_window(args.report_month)
    print(f"Content window: {start} <= date < {end}")
    names = (
        [name for name, config in sources.items() if config.get("enabled", True)]
        if args.all else ("cisa_alerts", "congress_gov")
    )
    totals = dict(ok=0, zero=0, failed=0, unavailable=0)
    total_items = 0
    for name in names:
        count, earliest, latest = "unknown", "-", "-"
        try:
            config = dict(sources[name], start_date=start, end_date=end)
            unavailable = False
            if config.get("type") == "congress_gov" or name == "congress_gov":
                key = config.get("api_key") or os.environ.get("CONGRESS_GOV_API_KEY") or _keyring_api_key()
                unavailable = not key
                config["api_key"] = key
            if unavailable:
                status = "unavailable"
                detail = "unavailable (no readable key; not a verified zero)"
            else:
                # Keep this a single read-only probe, like the original checker.
                result = get_fetcher(name, config).fetch()
                # Parse rather than echo arbitrary source text into this safe output.
                dates = [date.fromisoformat(item.published) for item in result.items if item.published]
                if dates:
                    earliest, latest = min(dates).isoformat(), max(dates).isoformat()
                count = len(result.items)
                total_items += count
                status = "ok" if count else "zero"
                detail = status
        except Exception as error:
            # Print only the exception class; never expose request internals.
            status = "failed"
            detail = f"failed ({type(error).__name__})"
        totals[status] += 1
        print(f"{name}: {count} items; earliest={earliest}; latest={latest}; {detail}")
    print(
        f"Summary: {sum(totals.values())} sources; {total_items} items; "
        + "; ".join(f"{name}={count}" for name, count in totals.items())
    )
    return 1 if totals["failed"] or totals["unavailable"] else 0


if __name__ == "__main__":
    sys.exit(main())
