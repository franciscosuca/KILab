#!/usr/bin/env bash
# Sync checker for the cv-generator skill: catalog (portable) <-> local install (personal).
# Rule book: ../SKILL.md (same skill). Read it before copying anything.
#
# Usage: sync.sh [--local <dir>]
#   CV_GENERATOR_SKILL_DIR   local install to compare against
#                            (default: ~/.pi/agent/skills/cv-generator)
#   CV_SYNC_PII_PATTERNS     optional file with personal grep -E patterns, one per line
#                            (default: ~/.config/cv-generator/sync-pii-patterns.txt)
#
# What it does: (1) guards the catalog against personal files/data, (2) scans for PII,
# (3) checks structural invariants (template<->build.py pairing, feature parity,
#     frontmatter), (4) prints an informational drift report.
#
# Exit codes: 0 = catalog clean (drift may still be listed), 1 = PII/invariant failure,
#             2 = usage/setup error.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG="${CV_GENERATOR_CATALOG_DIR:-$(cd "$HERE/../../cv-generator" && pwd)}"
LOCAL="${CV_GENERATOR_SKILL_DIR:-$HOME/.pi/agent/skills/cv-generator}"
PII_FILE="${CV_SYNC_PII_PATTERNS:-$HOME/.config/cv-generator/sync-pii-patterns.txt}"

if [ "${1:-}" = "--local" ]; then
  LOCAL="${2:?--local needs a path}"
  shift 2
fi

fail=0
note() { printf '%s\n' "$*"; }
bad()  { printf 'FAIL %s\n' "$*"; fail=1; }

[ -f "$CATALOG/SKILL.md" ] || { echo "catalog skill not found: $CATALOG" >&2; exit 2; }

TMP="$(mktemp -d /tmp/cvsync.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

# ---------------------------------------------------------------- 1. never-port guard
# These exist only in the local install; their presence here means a bad copy.
for f in assets/photo.jpg assets/photo.png assets/qr.png; do
  [ -e "$CATALOG/$f" ] && bad "personal asset in catalog: $f (remove it)"
done
# Any profile file must be the example template, never the real one.
find "$CATALOG" -name 'profile*.md' ! -name '*example*' 2>/dev/null | while IFS= read -r p; do
  bad "personal profile in catalog: ${p#"$CATALOG"/}"
done
# Note: the while-loop above runs in a subshell, so repeat the check without a pipe:
for p in "$CATALOG"/references/profile*.md; do
  [ -e "$p" ] || continue
  case "$p" in *example*) ;; *) bad "personal profile in catalog: ${p#"$CATALOG"/}" ;; esac
done

# ---------------------------------------------------------------- 2. PII scan
# a) generic patterns that are safe to keep in the repo (emails / long phone numbers),
#    skipping the sanctioned placeholder files.
pii_hits="$(grep -rInE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\+?[0-9]{1,3}[ /.-][0-9]{6,}' \
  --exclude='example-cv.json' --exclude='profile.example.md' "$CATALOG" 2>/dev/null || true)"
if [ -n "$pii_hits" ]; then
  printf '%s\n' "$pii_hits"
  bad "generic PII pattern hit (email/phone) in catalog"
else
  note "OK   no generic PII (emails/phones) in catalog"
fi

# b) private patterns (names, employers) from the out-of-repo file, if present.
if [ -f "$PII_FILE" ]; then
  priv_hit=0
  while IFS= read -r pat; do
    case "$pat" in ''|'#'*) continue ;; esac
    hits="$(grep -rInE "$pat" "$CATALOG" 2>/dev/null || true)"
    if [ -n "$hits" ]; then
      printf '%s\n' "$hits"
      bad "private PII pattern hit: /$pat/"
      priv_hit=1
    fi
  done < "$PII_FILE"
  [ "$priv_hit" -eq 0 ] && note "OK   no private PII patterns hit (from $PII_FILE)"
else
  note "note: no private pattern file at $PII_FILE (optional; see this skill's SKILL.md)"
fi

# ---------------------------------------------------------------- 3. structural invariants
# template <-> build.py pairing: the example must render with no unfilled {{slots}}.
cp "$CATALOG/assets/example-cv.json" "$TMP/cv.json"
if out="$(CV_GENERATOR_HOME="$TMP/home" python3 "$CATALOG/scripts/build.py" "$TMP/cv.json" "$TMP/out.html" 2>&1)"; then
  if grep -q '{{' "$TMP/out.html" 2>/dev/null; then
    bad "unfilled {{slots}} left in rendered HTML (template<->build.py mismatch)"
  else
    note "OK   template <-> build.py pairing (example renders, all slots filled)"
  fi
else
  bad "build.py failed on the example: $out"
fi

# v2 layout: sidebar must not carry the certifications/additional slots any more.
aside="$(sed -n '/<aside>/,/<\/aside>/p' "$CATALOG/assets/template.html")"
case "$aside" in
  *CERTIFICATIONS*) bad "sidebar still has {{CERTIFICATIONS}} (v2 layout regressed)" ;;
esac
case "$aside" in
  *ADDITIONAL*) bad "sidebar still has {{ADDITIONAL}} (v2 layout regressed)" ;;
esac
grep -q 'L_COMPETENCIES' "$CATALOG/assets/template.html" || bad "template lost the competencies slot"
grep -q '<section>' "$CATALOG/scripts/build.py" || bad "build.py lost the main-column additional renderer"

# feature parity: things the catalog must not lose again (they were once only local).
grep -q '"es"' "$CATALOG/scripts/build.py"                 || bad "es labels missing from scripts/build.py"
grep -q 'CV_GENERATOR_HOME' "$CATALOG/scripts/build.py"    || bad "CV_GENERATOR_HOME missing from scripts/build.py"
grep -q -- '--home' "$CATALOG/scripts/build.py"            || bad "--home missing from scripts/build.py"
grep -q -- '--home' "$CATALOG/scripts/cv.sh"               || bad "--home missing from scripts/cv.sh"
grep -q '| key | en | es | de |' "$CATALOG/references/schema.md" || bad "schema.md lost the es label column"
grep -q 'Wording rules (ATS' "$CATALOG/references/tailoring.md"  || bad "tailoring.md lost the ATS wording rules (§8)"

# frontmatter contract for other providers.
grep -q 'user-invocable: true' "$CATALOG/SKILL.md" || bad "SKILL.md lost 'user-invocable: true'"
grep -q 'argument-hint:' "$CATALOG/SKILL.md"       || bad "SKILL.md lost 'argument-hint'"
grep -q '^name: cv-generator$' "$CATALOG/SKILL.md" || bad "SKILL.md frontmatter name changed"

# ---------------------------------------------------------------- 4. drift report (informational)
if [ -d "$LOCAL" ]; then
  note "--- drift: catalog vs ${LOCAL/#$HOME/~} (classify each hit per this skill's SKILL.md) ---"
  diff -rq "$CATALOG" "$LOCAL" 2>/dev/null | sed "s|$HOME|~|g" || true
  note "--- expected only in local install: assets/photo.jpg, assets/qr.png, references/profile.md ---"
else
  note "note: local install not found at ${LOCAL/#$HOME/~} (set CV_GENERATOR_SKILL_DIR for drift report)"
fi

# ---------------------------------------------------------------- result
if [ "$fail" -ne 0 ]; then
  note "RESULT: FAIL — fix the failures above before syncing."
  exit 1
fi
note "RESULT: OK — catalog is clean. Review any drift above against sync-cv-generator/SKILL.md before copying."
