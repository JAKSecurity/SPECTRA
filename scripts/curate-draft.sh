#!/usr/bin/env bash
# scripts/curate-draft.sh — Stage 2c: Assemble markdown draft from curated JSON
# Usage: scripts/curate-draft.sh [curated_json] [month_label]
# Example: scripts/curate-draft.sh data/drafts/curated_2026-04.json "APRIL 2026"
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

CURATED_JSON="${1:-}"
MONTH_LABEL="${2:-}"

if [ -z "$CURATED_JSON" ]; then
    CURATED_JSON="data/drafts/curated_$(date -u +%Y-%m).json"
fi

if [ -z "$MONTH_LABEL" ]; then
    MONTH_LABEL=$(date -u +"%B %Y" | tr '[:lower:]' '[:upper:]')
fi

if [ ! -f "$CURATED_JSON" ]; then
    echo "Error: Curated JSON not found at $CURATED_JSON"
    echo "Run the curate scheduled task first."
    exit 1
fi

DRAFT_MD="data/drafts/$(date -u +%Y-%m)-SPECTRA.md"

echo "SPECTRA Draft — Stage 2c"
echo "  Curated JSON: $CURATED_JSON"
echo "  Month: $MONTH_LABEL"

PYTHONPATH="$PROJECT_DIR" python -c "
import json
from src.curate.draft import assemble_draft

with open('$CURATED_JSON') as f:
    items = json.load(f)

md = assemble_draft(items, '$MONTH_LABEL')

with open('$DRAFT_MD', 'w') as f:
    f.write(md)

print(f'  Draft written to $DRAFT_MD')
print(f'  {len(items)} items across sections')
"

echo ""
echo "Review the draft at: $DRAFT_MD"
echo "When satisfied, run: scripts/render.sh $DRAFT_MD"
