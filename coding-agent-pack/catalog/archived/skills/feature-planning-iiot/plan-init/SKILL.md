---
name: plan-init
description: "Initialize a repository's configured plan lifecycle. Use once to create the index and drafts, next, open, done, and discarded folders without moving legacy plans."
argument-hint: "No arguments"
user-invocable: true
---

# Initialize Plans

Read `.github/skills/plan-spec/SKILL.md` first. Run this once for the repository or workspace. Resolve `PLAN_ROOT` from repository documentation or configuration, or require it from the environment when no convention exists. This creates bookkeeping only; it does not change product code, initialize Git, or commit anything.

## Procedure

1. Confirm the repository or workspace contains `.github/skills/plan-spec/SKILL.md` and resolve `PLAN_ROOT`.
2. Inventory existing plan bundles and lifecycle folders. Treat standalone Markdown directly under a lifecycle folder as legacy and do not move it automatically. A canonical file nested one level below a lifecycle folder is the plan owner; supporting files are not separate plans.
3. Create the five missing lifecycle folders.
4. Create `PLAN_ROOT/README.md` only if absent. If it exists, preserve its content and add only missing lifecycle sections.
5. Index legacy files under `Unclassified legacy plans`. Ask the Prompter before classifying or moving any of them.
6. Verify the layout and report every created path. New plans must use `iiot-<NUMBER>-<NAME>/<iiot-<NUMBER>-<NAME>.md`; use the corresponding `iiot-XXXX-<inferred-name>` bundle when the number is not supplied. Do not rename legacy files or make a commit.

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

Run these preflight and verification commands after setting the plan root. Use workspace file tools to create the folders and README.

```bash
PLAN_ROOT="${PLAN_ROOT:?Set PLAN_ROOT to the configured planning root}"
test -f .github/skills/plan-spec/SKILL.md
find "$PLAN_ROOT" -maxdepth 4 -type f -name '*.md' -print 2>/dev/null | sort
mkdir -p "$PLAN_ROOT"/{drafts,next,open,done,discarded}
find "$PLAN_ROOT" -maxdepth 1 -type d -print | sort
find "$PLAN_ROOT" -maxdepth 3 -type f -name '*.md' -print | sort
```

Never overwrite a non-empty index, relocate a legacy plan, or normalize its format without showing the Prompter the proposed classification first.
