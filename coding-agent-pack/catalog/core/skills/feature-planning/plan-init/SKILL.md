---
name: plan-init
description: "Initialize a repository's configured plan lifecycle. Use once to create the index and drafts, next, open, done, and discarded folders without moving legacy plans."
argument-hint: "No arguments"
user-invocable: true
---

# Initialize Plans

Read the sibling `plan-spec/SKILL.md` first. Before inspecting or creating anything, pass its `PLAN_ROOT` fail-closed gate. If no valid absolute path is available from the current request, explicit repository/workspace configuration, or the current agent environment, ask the user for `PLAN_ROOT` and stop. Do not guess or create a candidate root. Once supplied, this skill may initialize that exact root. This creates bookkeeping only; it does not change product code, initialize Git, or commit anything.

## Procedure

1. Confirm the installed feature-planning skill contains the sibling `plan-spec/SKILL.md`; resolve and validate `PLAN_ROOT` before any lifecycle-folder inventory or filesystem mutation. If it is missing, ask the user for an absolute path and stop.
2. Inventory existing plan bundles and lifecycle folders. Treat standalone Markdown directly under a lifecycle folder as legacy and do not move it automatically. A canonical file nested one level below a lifecycle folder is the plan owner; supporting files are not separate plans.
3. Create the five missing lifecycle folders.
4. Create `PLAN_ROOT/README.md` only if absent. If it exists, preserve its content and add only missing lifecycle sections.
5. Index legacy files under `Unclassified legacy plans`. Ask the Prompter before classifying or moving any of them.
6. Verify the layout and report every created path. New plans must use `plan-<NUMBER>-<NAME>/<plan-<NUMBER>-<NAME>.md`; use the corresponding `plan-XXXX-<inferred-name>` bundle when the number is not supplied. Do not rename legacy files or make a commit.

The index uses these sections in order:

```markdown
# Task Plans

## Next
## Open
## Drafts
## Blocked
## Recently Done
## Discarded
## Unclassified Legacy Plans
```

Each entry is one checkbox line with plan link, title, external identifier when present, owner, last update, and a short blocker or next action. Use `Owner` when no owner has been assigned. Do not copy full plan summaries into the index.

## Commands

Run these commands only after the `PLAN_ROOT` gate passes. Use workspace file tools to create the folders and README.

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be supplied as an absolute path; ask the user and stop.\n' >&2
  exit 2
fi
test -n "$(find . -type f -path '*/plan-spec/SKILL.md' -print -quit)"
find "$PLAN_ROOT" -maxdepth 4 -type f -name '*.md' -print 2>/dev/null | sort
mkdir -p "$PLAN_ROOT"/{drafts,next,open,done,discarded}
find "$PLAN_ROOT" -maxdepth 1 -type d -print | sort
find "$PLAN_ROOT" -maxdepth 3 -type f -name '*.md' -print | sort
```

Never overwrite a non-empty index, relocate a legacy plan, or normalize its format without showing the Prompter the proposed classification first.
