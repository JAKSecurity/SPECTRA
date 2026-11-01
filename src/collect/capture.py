"""Retain short-feed snapshots for the next issue, without curation or delivery."""
import argparse
from datetime import date

from .runner import run_collect


def run_capture(config_path="src/collect/config.yaml", output_base="data/sources", *, today=None):
    today = today or date.today()
    year, month = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return run_collect(config_path, output_base, f"{year:04d}-{month:02d}", capture=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_path", nargs="?", default="src/collect/config.yaml")
    parser.add_argument("output_base", nargs="?", default="data/sources")
    args = parser.parse_args()
    results = run_capture(args.config_path, args.output_base)
    for result in results:
        print(f"{result['source']}: {result['status']}")
    return int(any(r["status"] in ("error", "unavailable") for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
