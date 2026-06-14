#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/www/wwwlogs"
LOG_FILE="${LOG_DIR}/weread_scrapy_daily.log"
LOCK_FILE="/tmp/weread_scrapy_daily.lock"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

{
  echo "========== $(date '+%Y-%m-%d %H:%M:%S') start =========="
  flock -n 9 || {
    echo "Another weread crawler task is still running. Skip this run."
    exit 0
  }
  ./run_weread_crawler.sh
  echo "========== $(date '+%Y-%m-%d %H:%M:%S') finished =========="
} 9>"$LOCK_FILE" >> "$LOG_FILE" 2>&1
