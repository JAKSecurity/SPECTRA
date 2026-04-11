import glob
import json
import os
import sys


def load_items(source_dir: str) -> list:
    """Load all items from JSON files in a source directory."""
    items = []
    for filepath in sorted(f for f in glob.glob(os.path.join(source_dir, "*.json")) if not os.path.basename(f).startswith("_")):
        with open(filepath) as f:
            data = json.load(f)
            source_name = data.get("source", "unknown")
            for item in data["items"]:
                item["_source"] = source_name
                items.append(item)
    return items


def deduplicate(items: list) -> list:
    """Remove items with duplicate URLs, keeping first occurrence."""
    seen = set()
    unique = []
    for item in items:
        url = item.get("url", "")
        if url not in seen:
            seen.add(url)
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
