import argparse
import json
import os
import re
import time
from datetime import date, datetime, timezone

import yaml

from .fetchers import get_fetcher


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def _configured_secrets(config: dict) -> set[str]:
    """Collect nonempty credential values without changing source configuration."""
    secrets = set()
    for name, value in config.items():
        if isinstance(value, dict):
            secrets.update(_configured_secrets(value))
        elif isinstance(value, str) and value and name.lower() in {
            "api_key", "x-api-key", "token", "api_token", "access_token",
            "password", "secret", "client_secret", "authorization",
        }:
            secrets.add(value)
    return secrets


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
    secrets = _configured_secrets(config)
    environment_key = os.environ.get("CONGRESS_GOV_API_KEY")
    if environment_key:
        secrets.add(environment_key)
    secret_pattern = (
        re.compile("|".join(re.escape(value) for value in sorted(secrets, key=len, reverse=True)))
        if secrets else None
    )
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
            # Core sources get one fresh attempt before an empty/error is persisted.
            # WHY: a transient CISA feed failure must not erase a monthly source (003).
            for attempt in range(2 if source_config.get("core", False) else 1):
                try:
                    result = fetcher.fetch()
                    if (result.status == "unavailable" or result.items
                            or attempt == 1 or not source_config.get("core", False)):
                        break
                except Exception:
                    if attempt == 1 or not source_config.get("core", False):
                        raise
                time.sleep(1)
            status = result.status
            if status == "ok" and (
                result.page_cap_reached or result.window_start_reached is False
            ):
                status = "partial"
            result.status = status
            filepath = fetcher.save(result, month_dir)
            results.append(
                {
                    "source": name,
                    "status": status,
                    "items": None if status == "unavailable" else len(result.items),
                    "file": filepath,
                    "pages_fetched": result.pages_fetched,
                    "page_cap_reached": result.page_cap_reached,
                    "window_start_reached": result.window_start_reached,
                }
            )
        except Exception as e:
            # WHY: the 2026-10-28 workshop audit found exception text leaks keys
            # into results, health warnings and console output. Preserve diagnostics.
            error = str(e)
            if secret_pattern is not None:
                error = secret_pattern.sub("[REDACTED]", error)
            results.append({
                "source": name, "status": "error", "error": error,
                "pages_fetched": None, "page_cap_reached": None,
                "window_start_reached": None,
            })

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
    # WHY: partial coverage still collected usable items; preserve transport totals.
    ok = [r for r in results if r["status"] in ("ok", "partial")]
    partial = [r for r in results if r["status"] == "partial"]
    unavailable = [r for r in results if r["status"] == "unavailable"]
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
            "partial": len(partial),
            "unavailable": len(unavailable),
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
    if partial:
        report["warnings"] = report.get("warnings", []) + [
            f"{r['source']}: partial coverage (page cap reached or window start not reached)"
            for r in partial
        ]
    if unavailable:
        report["warnings"] = report.get("warnings", []) + [
            f"{r['source']}: unavailable; item count unknown (not a verified zero)"
            for r in unavailable
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
        if r["status"] in ("ok", "partial"):
            print(f"  {r['status'].upper()}  {r['source']}: {r['items']} items -> {r['file']}")
        elif r["status"] == "unavailable":
            print(f"  UNAVAILABLE {r['source']}: unknown items (not a verified zero)")
        else:
            print(f"  ERR {r['source']}: {r['error']}")

    ok_count = sum(1 for r in results if r["status"] in ("ok", "partial"))
    err_count = sum(1 for r in results if r["status"] == "error")
    partial_count = sum(1 for r in results if r["status"] == "partial")
    unavailable_count = sum(1 for r in results if r["status"] == "unavailable")
    total_items = sum(r["items"] for r in results if r["status"] in ("ok", "partial"))
    print(f"\nDone: {ok_count} succeeded ({partial_count} partial), {err_count} failed, "
          f"{unavailable_count} unavailable, {total_items} total items")

    # Report empty sources as warnings
    empty = [r for r in results if r["status"] in ("ok", "partial") and r["items"] == 0]
    if empty:
        print("\nWarnings:")
        for r in empty:
            print(f"  {r['source']}: returned 0 items (feed may be stale)")


if __name__ == "__main__":
    main()
