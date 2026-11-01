import glob
import json
import os
import sys

from src.collect.history import snapshot_time


def load_items(source_dir: str) -> list:
    """Load all items from JSON files in a source directory."""
    items = []
    snapshots = []
    for filepath in sorted(f for f in glob.glob(os.path.join(source_dir, "*.json")) if not os.path.basename(f).startswith("_")):
        with open(filepath) as f:
            data = json.load(f)
            snapshots.append(data)
    captured = {data.get("source") for data in snapshots if data.get("capture")}
    for data in snapshots:
        source_name = data.get("source", "unknown")
        for item in data["items"]:
            item["_source"] = source_name
            if source_name in captured:
                item["_fetched_at"] = snapshot_time(data)
            items.append(item)
    return items


def deduplicate(items: list) -> list:
    """Merge captured identities by recency, then keep first entries at a URL.

    Nonempty IDs identify entries. If either ID is missing, compare titles
    (case and whitespace normalized) and publication dates instead. Both
    fallback fields must be present; incomplete metadata cannot prove a repeat.
    """
    # WHY: latest publisher identity survives URL changes across captures (docs/adr/0002-frequent-capture-for-short-feeds.md).
    latest = {}
    for item in items:
        if "_fetched_at" in item and item.get("id"):
            key = (item["_source"], item["id"])
            if key not in latest or item["_fetched_at"] >= latest[key]["_fetched_at"]:
                latest[key] = item
    items = [item for item in items if "_fetched_at" not in item or not item.get("id")
             or latest[(item["_source"], item["id"])] is item]
    seen_by_url = {}
    unique = []
    for item in items:
        url = item.get("url", "")
        item_id = (item.get("id") or "").strip()
        title = " ".join((item.get("title") or "").casefold().split())
        published = (item.get("published") or "").strip()
        entries = seen_by_url.setdefault(url, [])
        duplicate = any(
            item_id == previous_id if item_id and previous_id else
            bool(title and published and (title, published) == (previous_title, previous_date))
            for previous_id, previous_title, previous_date in entries
        )
        if not duplicate:
            entries.append((item_id, title, published))
            unique.append(item)
    return unique


def prep_items(source_dir: str, output_path: str) -> list:
    """Load, deduplicate, and write prepped items for curate task."""
    items = load_items(source_dir)
    items = deduplicate(items)

    # Strip internal _source into a clean format for the curate task
    prepped = []
    for item in items:
        prepped.append({
            "id": item["id"],
            "title": item["title"],
            "url": item.get("url", ""),
            "published": item.get("published", ""),
            "summary": item.get("summary", "")[:500],
            "category_hint": item.get("category_hint", ""),
            "source": item.get("_source", "unknown"),
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(prepped, f, indent=2)

    return prepped


def main():
    source_dir = sys.argv[1] if len(sys.argv) > 1 else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not source_dir:
        print("Usage: python -m src.curate.curate <source_dir> <output_json>")
        sys.exit(1)

    if not output_path:
        output_path = f"data/drafts/prepped_{os.path.basename(source_dir)}.json"

    print(f"SPECTRA Prep — loading items from {source_dir}")
    prepped = prep_items(source_dir, output_path)
    print(f"  Prepped {len(prepped)} items -> {output_path}")
    print()
    print("Next: run the curate scheduled task or manually curate the prepped items.")


if __name__ == "__main__":
    main()
