---
name: plan-add
description: "Capture a task, issue, bug, idea, or request as a concise draft plan with source links and a local context snapshot. Use before investigation or design decisions are complete."
argument-hint: "<task, issue key, URL, or idea>"
user-invocable: true
---

# Add A Draft Plan

Read `.github/skills/plan-spec/SKILL.md` first and resolve `PLAN_ROOT` from it. Capture the request quickly without pretending the design is settled. Do not implement product code.

## Procedure

1. Extract the problem, desired result, examples, constraints, affected area, source ticket or page, and any named dependency from the request.
2. Search all lifecycle folders and legacy plan bundles for the ticket key and distinctive terms. Update the matching canonical draft instead of creating a duplicate.
3. If an external issue or documentation reference is present, read it through the available connector. Preserve its exact summary, identifiers, and relevant version information.
4. Snapshot only the likely owning repositories: current branch, dirty files, remote, and recent relevant commits. Never overwrite or clean user changes.
5. Search recent local agent sessions when they may explain prior decisions. Search external conversations only when an authorized connector is actually available; otherwise record that they were not checked.
6. Create a plan bundle in `$PLAN_ROOT/drafts/<plan-slug>/` using the plan specification: `iiot-<NUMBER>-<NAME>/iiot-<NUMBER>-<NAME>.md` when an issue number is supplied; otherwise use `iiot-XXXX-<inferred-name>/iiot-XXXX-<inferred-name>.md`. Infer a lowercase hyphenated name from the request, limited to four words. Never guess a missing number. Create `context/`, `workflows/`, and `work-packages/` directories; the latter two remain empty.
7. Preserve the incoming request and supplied references in `context/request.md`. Create the canonical Markdown file with YAML frontmatter, the issue tag, `Status`, `Summary`, `Diagram`, `Steps`, `Verification`, `Estimations`, and `Related documents`. Include empty `Context`, `Work packages`, and `Workflows` subsections under Related documents. Do not create workflow or work-package files during `/plan-add`. Use the canonical structure from `plan-spec` rather than the minimum legacy draft sections.
8. Add or refresh its single-line entry in `$PLAN_ROOT/README.md`. Do not commit.

Use the Prompter's own task language: problem first, then desired workflow or state, then constraints or alternatives. Keep screenshots and reproduction steps when supplied.

## Commands

```bash
PLAN_ROOT="${PLAN_ROOT:?Set PLAN_ROOT to the configured planning root}"
grep -RniE '<issue-key|distinctive-terms>' "$PLAN_ROOT" 2>/dev/null
date +%F
git -C <repo> status --short --branch
git -C <repo> remote -v
git -C <repo> log --all -n 10 --date=short --format='%ad %h %s'
<issue-tracker-lookup-command>
<documentation-lookup-command>
find "$PLAN_ROOT" -maxdepth 4 -type f -name '*.md' -print | sort
```

Use the available local session-history tool with a bounded query filtered by repository and distinctive terms when recent context is relevant. Never put credentials or raw secret-bearing conversation text into a plan.

## Draft Gate

Leave the file in `drafts` when the owner, code path, desired behavior, or implementation decision is unknown. `/plan-add` records work; `/plan-write` proves and designs it.