#!/usr/bin/env bash
# scripts/render.sh — Stage 3: Markdown draft -> PDF
# Usage: scripts/render.sh [draft_md_path] [output_pdf_path]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

DRAFT_MD="${1:-}"
OUTPUT_PDF="${2:-}"

if [ -z "$DRAFT_MD" ]; then
    # Default to current month draft
    DRAFT_MD="data/drafts/$(date -u +%Y-%m)-SPECTRA.md"
fi

if [ -z "$OUTPUT_PDF" ]; then
    mkdir -p output
    OUTPUT_PDF="output/$(date -u +%Y-%m)-SPECTRA.pdf"
fi

if [ ! -f "$DRAFT_MD" ]; then
    echo "Error: Draft not found at $DRAFT_MD"
    echo "Run scripts/curate.sh first."
    exit 1
fi

PYTHONPATH="$PROJECT_DIR" python -m src.render.render "$DRAFT_MD" "$OUTPUT_PDF"
