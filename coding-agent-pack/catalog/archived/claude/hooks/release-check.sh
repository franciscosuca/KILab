#!/bin/bash
# Release-check hook for Claude Code
# Runs local quality gates before Claude can finish.
# Exit code 2 = block stop and force Claude to fix issues.

set -euo pipefail

INPUT=$(cat)

# If already in a forced-continuation loop, don't block again (avoid infinite loops)
if echo "$INPUT" | grep -q '"stop_hook_active"\s*:\s*true'; then
  exit 0
fi

ERRORS=""

# Only run checks if scripts exist in package.json
if [ -f "package.json" ]; then
  has_script() {
    node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts['$1'] ? 0 : 1)" 2>/dev/null
  }

  if has_script "lint"; then
    echo "Running lint..."
    if ! npm run lint --silent 2>&1; then
      ERRORS+="❌ Lint failed\n"
    fi
  fi

  if has_script "test"; then
    echo "Running tests..."
    if ! npm test --silent 2>&1; then
      ERRORS+="❌ Tests failed\n"
    fi
  fi

  if has_script "build"; then
    echo "Running build..."
    if ! npm run build --silent 2>&1; then
      ERRORS+="❌ Build failed\n"
    fi
  fi
fi

if [ -n "$ERRORS" ]; then
  echo ""
  echo "Release check failed:"
  echo -e "$ERRORS"
  echo "Fix the issues above before completing."
  exit 2
fi

exit 0
