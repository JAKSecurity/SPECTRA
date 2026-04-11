#!/usr/bin/env bash
# scripts/collect.sh — Stage 1: Fetch sources
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
PYTHONPATH="$PROJECT_DIR" python -m src.collect.runner \
    "${1:-src/collect/config.yaml}" \
    "${2:-data/sources}"
