#!/usr/bin/env bash
# scripts/collect.sh — Stage 1: Fetch sources
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

PYTHONPATH="$PROJECT_DIR" "$PYTHON_BIN" -m src.collect.runner \
    "${1:-src/collect/config.yaml}" \
    "${2:-data/sources}" \
    "${@:3}"
