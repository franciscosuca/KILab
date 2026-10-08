#!/usr/bin/env bash
# One-shot: JSON -> HTML -> fit to one page -> PDF.
# Usage: cv.sh <cv.json> [out-basename]     (output goes next to the JSON: <basename>.html / .pdf)
#        cv.sh --home                       (print the user-data directory and which files exist)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--home" ]; then exec python3 "$HERE/build.py" --home; fi   # user-data dir status
JSON="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
BASE="${2:-$(basename "$JSON" .json)}"
OUT="$(dirname "$JSON")"

# Playwright is installed once into a cache dir (not into the user's project).
export CV_PW_DIR="${CV_PW_DIR:-$HOME/.cache/cv-generator}"
if [ ! -d "$CV_PW_DIR/node_modules/playwright" ]; then
  echo "First run: installing Playwright + Chromium into $CV_PW_DIR (one-time, ~100 MB)..." >&2
  mkdir -p "$CV_PW_DIR" && (cd "$CV_PW_DIR" && npm init -y >/dev/null 2>&1 && npm i playwright >/dev/null 2>&1 && npx playwright install chromium >&2)
fi

python3 "$HERE/build.py" "$JSON" "$OUT/$BASE.html"
node "$HERE/fit.mjs" "$OUT/$BASE.html" "$OUT/$BASE.pdf"
