#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PACK_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
CATALOG="$PACK_ROOT/catalog"

failures=0
check() {
  if "$@"; then
    printf '✅ %s\n' "$*"
  else
    printf '❌ %s\n' "$*"
    failures=$((failures + 1))
  fi
}

check test -d "$CATALOG/core/agents"
check test -d "$CATALOG/core/skills"
check test -d "$CATALOG/adapters/copilot"
check test -d "$CATALOG/adapters/claude"
check test -d "$CATALOG/adapters/pi"
check test -d "$CATALOG/archived"
check test -x "$SCRIPT_DIR/install-pack.sh"
check bash -n "$SCRIPT_DIR/install-pack.sh"

while IFS= read -r -d '' file; do
  check grep -q '^---[[:space:]]*$' "$file"
  check grep -q '^name:' "$file"
  check grep -q '^description:' "$file"
done < <(find "$CATALOG/core/agents" -maxdepth 1 -type f -name '*.md' -print0)

while IFS= read -r -d '' file; do
  check grep -q '^---[[:space:]]*$' "$file"
  check grep -q '^name:' "$file"
  check grep -q '^description:' "$file"
done < <(find "$CATALOG/core/skills" -type f -name 'SKILL.md' -print0)

if rg -n -i '(/Users/|app-wizard|seal-module-opcua-client|Onboarding_Wizard_Semantic_Release|pipelines/Semantic_Release)' \
  "$CATALOG/core" >/dev/null; then
  printf '❌ core content contains project-specific paths or pipeline names\n'
  failures=$((failures + 1))
else
  printf '✅ core content contains no known project-specific paths\n'
fi

if find "$CATALOG/core" -type f \( -name '*opcua*' -o -name '*protocol*' \) | grep -q .; then
  printf '❌ project-specific OPCUA/protocol content is present in core\n'
  failures=$((failures + 1))
else
  printf '✅ project-specific OPCUA/protocol content is archived\n'
fi

if [ "$failures" -gt 0 ]; then
  printf '\nValidation failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf '\nPack validation passed.\n'
