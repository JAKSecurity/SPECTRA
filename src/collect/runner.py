import json
import os
import sys
from datetime import datetime, timezone

import yaml

from .fetchers import get_fetcher


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_collect(config_path: str, output_base: str = "data/sources") -> list:
    """Run all enabled fetchers and write JSON output."""
    config = load_config(config_path)
    month_dir = os.path.join(
        output_base, datetime.now(timezone.utc).strftime("%Y-%m")
    )
    os.makedirs(month_dir, exist_ok=True)

    results = []
    for name, source_config in config["sources"].items():
        if not source_config.get("enabled", True):
            continue
        try:
            fetcher = get_fetcher(name, source_config)
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
    _write_health_report(results, month_dir)

    return results


def _write_health_report(results: list, month_dir: str):
    """Save a health report JSON summarizing source fetch results."""
    ok = [r for r in results if r["status"] == "ok"]
    errors = [r for r in results if r["status"] == "error"]
    empty = [r for r in ok if r["items"] == 0]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    config_path = sys.argv[1] if len(sys.argv) > 1 else "src/collect/config.yaml"
    output_base = sys.argv[2] if len(sys.argv) > 2 else "data/sources"

    print(f"SPECTRA Collect \u2014 fetching sources from {config_path}")
    results = run_collect(config_path, output_base)

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
