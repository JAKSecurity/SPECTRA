"""Read-only live check for the two maintained public sources; prints counts only."""
import argparse
import sys
from pathlib import Path

# Allow invocation by absolute filename from the dispatcher's native checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.collect.fetchers import get_fetcher
from src.collect.fetchers.congress_gov import _keyring_api_key
from src.collect.runner import load_config, report_window
import os


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-month", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = load_config(str(root / "src/collect/config.yaml"))["sources"]
    start, end = report_window(args.report_month)
    print(f"Content window: {start} <= date < {end}")
    missing_or_failed = False
    for name in ("cisa_alerts", "congress_gov"):
        config = dict(sources[name], start_date=start, end_date=end)
        if name == "congress_gov":
            key = os.environ.get("CONGRESS_GOV_API_KEY") or _keyring_api_key()
            if not key:
                print("congress_gov: unavailable (no readable key; not a verified zero)")
                missing_or_failed = True
                continue
            config["api_key"] = key
        try:
            result = get_fetcher(name, config).fetch()
            print(f"{name}: {len(result.items)} items")
        except Exception as error:
            # Print only the exception class; never expose request internals.
            print(f"{name}: live check failed ({type(error).__name__})")
            missing_or_failed = True
    return 1 if missing_or_failed else 0


if __name__ == "__main__":
    sys.exit(main())
