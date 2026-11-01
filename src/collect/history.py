"""Shared, read-only coverage assessment for retained source snapshots."""
import json
from datetime import datetime
from pathlib import Path


def snapshot_time(snapshot):
    return datetime.fromisoformat(snapshot["fetched_at"].replace("Z", "+00:00")).timestamp()


def source_snapshots(month_dir, source):
    snapshots = []
    for path in sorted(Path(month_dir).glob("*.json")):
        if path.name.startswith("_"):
            continue
        snapshot = json.loads(path.read_text())
        if snapshot.get("source") == source and snapshot.get("status", "ok") in ("ok", "partial"):
            snapshots.append(snapshot)
    return snapshots


def capture_coverage(month_dir, source, current, start, end):
    """Return None for legacy folders, otherwise aggregate boundary and gaps.

    Raw snapshot coverage must stay raw: an aggregate boundary copied into a
    later snapshot would falsely bridge a real rollover gap.
    """
    # WHY: legacy monthly runs never read retained snapshots (ADR 0002).
    if not any(Path(month_dir).glob(f"{source}_capture_*.json")):
        return None
    snapshots = source_snapshots(month_dir, source)
    if not any(s.get("capture") for s in snapshots):
        return None
    snapshots.append(current)
    snapshots.sort(key=snapshot_time)
    reached = any(s.get("window_start_reached") is True for s in snapshots)
    ledger_path = Path(month_dir) / "_captures.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    # A later edit/backfill cannot erase an already observed rollover.
    gaps = list(ledger.get(source, {}).get("gaps", []))
    previous = None
    for snapshot in snapshots:
        dates = [item["published"] for item in snapshot["items"]
                 if start <= item.get("published", "") < end]
        if not dates:
            continue
        oldest, newest = min(dates), max(dates)
        if previous and oldest > previous:
            gap = {"after": previous, "before": oldest}
            if gap not in gaps:
                gaps.append(gap)
        previous = newest
    return {"window_start_reached": reached, "gaps": gaps}


def gap_warning(gaps):
    return "; ".join(f"rollover gap after {g['after']} before {g['before']}" for g in gaps)


def record_coverage(month_dir, source, coverage):
    path = Path(month_dir) / "_captures.json"
    ledger = json.loads(path.read_text()) if path.exists() else {}
    ledger[source] = coverage
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(ledger, indent=2))
    temporary.replace(path)
