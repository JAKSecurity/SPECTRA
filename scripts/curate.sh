#!/usr/bin/env bash
# scripts/curate.sh — Stage 2a: Prep source items for curation
# Usage: scripts/curate.sh [source_dir] [prepped_json]
# Example: scripts/curate.sh data/sources/2026-04
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

SOURCE_DIR="${1:-}"

if [ -z "$SOURCE_DIR" ]; then
    SOURCE_DIR="data/sources/$(date -u +%Y-%m)"
fi

DRAFT_DIR="data/drafts"
mkdir -p "$DRAFT_DIR"

REPORT_MONTH="$(basename "$SOURCE_DIR")"
PREPPED_JSON="${2:-$DRAFT_DIR/prepped_$REPORT_MONTH.json}"

echo "SPECTRA Prep — Stage 2a"
echo "  Source dir: $SOURCE_DIR"

PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

PYTHONPATH="$PROJECT_DIR" "$PYTHON_BIN" -m src.curate.curate "$SOURCE_DIR" "$PREPPED_JSON"

echo ""
echo "Prepped items written to: $PREPPED_JSON"
echo ""
echo "Next: Run the SPECTRA curate scheduled task, or manually curate."
echo "Then: scripts/curate-draft.sh to assemble the markdown draft."
