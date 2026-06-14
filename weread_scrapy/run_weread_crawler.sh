#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
fi

if [ -z "${WEREAD_API_KEY:-}" ]; then
  echo "WEREAD_API_KEY is missing. Please edit .env first." >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"

exec "$PYTHON_BIN" -m scrapy crawl weread_api "$@"
