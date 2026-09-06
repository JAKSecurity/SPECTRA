import argparse
import json
import os
from datetime import date, datetime, timezone

import yaml

from .fetchers import get_fetcher


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def report_window(report_month: str) -> tuple[str, str]:
    """Return the previous calendar month's inclusive/exclusive date window."""
    report_year, report_month_number = map(int, report_month.split("-"))
    report_start = date(report_year, report_month_number, 1)
    if report_month_number == 1:
        content_start = date(report_year - 1, 12, 1)
    else:
        content_start = date(report_year, report_month_number - 1, 1)
    return content_start.isoformat(), report_start.isoformat()


def run_collect(
    config_path: str,
    output_base: str = "data/sources",
    report_month: str | None = None,
) -> list:
    """Run all enabled fetchers and write JSON output."""
    config = load_config(config_path)
    report_month = report_month or datetime.now(timezone.utc).strftime("%Y-%m")
    start_date, end_date = report_window(report_month)
    month_dir = os.path.join(output_base, report_month)
    os.makedirs(month_dir, exist_ok=True)

    results = []
    for name, source_config in config["sources"].items():
        if not source_config.get("enabled", True):
            continue
        try:
            windowed_config = dict(source_config)
            windowed_config["start_date"] = start_date
            windowed_config["end_date"] = end_date
            fetcher = get_fetcher(name, windowed_config)
            result = fetcher.fetch()
            filepath = fetcher.save(result, month_dir)
            results.append(
                {
                    "source": name,
                    "status": "ok",
                    "items": len(result.items),
                    "file": filepath,
                }
            )
        except Exception as e:
            results.append({"source": name, "status": "error", "error": str(e)})

    # Write health report
    _write_health_report(results, month_dir, report_month, start_date, end_date)

    return results


def _write_health_report(
    results: list,
    month_dir: str,
    report_month: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Save a health report JSON summarizing source fetch results."""
    ok = [r for r in results if r["status"] == "ok"]
    errors = [r for r in results if r["status"] == "error"]
    empty = [r for r in ok if r["items"] == 0]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_month": report_month,
        "content_window": {"start": start_date, "end_exclusive": end_date},
        "summary": {
            "total_sources": len(results),
            "succeeded": len(ok),
            "failed": len(errors),
            "empty": len(empty),
            "total_items": sum(r["items"] for r in ok),
        },
        "sources": results,
    }

    if errors:
        report["warnings"] = [
            f"{r['source']}: {r['error']}" for r in errors
        ]
    if empty:
        report["warnings"] = report.get("warnings", []) + [
            f"{r['source']}: returned 0 items (feed may be stale or broken)"
            for r in empty
        ]

    report_path = os.path.join(month_dir, "_health.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report_path


def main():
    parser = argparse.ArgumentParser(description="Collect SPECTRA source material")
    parser.add_argument("config_path", nargs="?", default="src/collect/config.yaml")
    parser.add_argument("output_base", nargs="?", default="data/sources")
    parser.add_argument(
        "--report-month",
        help="Issue month in YYYY-MM form; source window is the previous calendar month",
    )
    args = parser.parse_args()

    report_month = args.report_month or datetime.now(timezone.utc).strftime("%Y-%m")
    start_date, end_date = report_window(report_month)
    print(f"SPECTRA Collect - report {report_month}, content {start_date} through {end_date} (exclusive)")
    print(f"Fetching sources from {args.config_path}")
    results = run_collect(args.config_path, args.output_base, report_month=report_month)

    for r in results:
        if r["status"] == "ok":
            print(f"  OK  {r['source']}: {r['items']} items -> {r['file']}")
        else:
            print(f"  ERR {r['source']}: {r['error']}")

    ok_count = sum(1 for r in results if r["status"] == "ok")
    err_count = sum(1 for r in results if r["status"] == "error")
    total_items = sum(r["items"] for r in results if r["status"] == "ok")
    print(f"\nDone: {ok_count} succeeded, {err_count} failed, {total_items} total items")

    # Report empty sources as warnings
    empty = [r for r in results if r["status"] == "ok" and r["items"] == 0]
    if empty:
        print("\nWarnings:")
        for r in empty:
            print(f"  {r['source']}: returned 0 items (feed may be stale)")


if __name__ == "__main__":
    main()
