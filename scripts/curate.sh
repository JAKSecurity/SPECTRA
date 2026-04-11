#!/usr/bin/env bash
# scripts/curate.sh — Stage 2a: Prep source items for curation
# Usage: scripts/curate.sh [source_dir]
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

PREPPED_JSON="$DRAFT_DIR/prepped_$(date -u +%Y-%m).json"

echo "SPECTRA Prep — Stage 2a"
echo "  Source dir: $SOURCE_DIR"

PYTHONPATH="$PROJECT_DIR" python -m src.curate.curate "$SOURCE_DIR" "$PREPPED_JSON"

echo ""
echo "Prepped items written to: $PREPPED_JSON"
echo ""
echo "Next: Run the SPECTRA curate scheduled task, or manually curate."
echo "Then: scripts/curate-draft.sh to assemble the markdown draft."
