---
name: plan-sync
description: "Synchronize open plans with reviews, CI, external work items, releases, and deployments; move only verified work to done and confirmed abandoned work to discarded."
argument-hint: "[plan name or ticket key]"
user-invocable: true
---

# Synchronize Plans

Read the sibling `plan-spec/SKILL.md` first. Before selecting or inspecting plans, pass its `PLAN_ROOT` fail-closed gate. If no valid absolute root is available, ask the user for it and stop without scanning or changing plans. Synchronization compares recorded intent with what actually landed. A merged PR alone is not always done.

## Procedure

1. Resolve and validate `PLAN_ROOT` before any lifecycle scan. If it is absent or invalid, ask the user for an absolute path and stop. Then select the requested canonical plan or every plan bundle in `$PLAN_ROOT/open/`. Do not treat supporting files as separate plans.
2. Read the canonical plan's acceptance criteria, verification commands, dependencies, PRs, promised release/deployment, and Execution scope when present. Read related work packages as supporting scope, not separate lifecycle owners.
3. Check each review's state, latest commit, unresolved comments, required policies/checks, and merge result. For scoped work, associate every result with its WP, branch/base, and commit; do not use one WP's passing checks to verify another. Check the linked external work item and release evidence such as a release marker, release-system record, deployed version, or documented smoke test when the plan requires it.
4. Compare changed files and reported results with every plan phase. Reconcile each dispatched WP's acceptance evidence and mark it `verified` only when its own required criteria/checks/reviews and WP-specific release promises pass under `plan-spec`. Otherwise retain its actual progress and named wait. Record omissions, changed scope, regressions that invalidate prior verification, and remaining WPs in `Outcome`; do not rewrite the original plan to match the PR, approve the next WP, or erase deferred scope.
5. Apply one result:
   - keep in `open` when any required WP is planned, ready, in-progress, in-review, blocked, or unverified, or when combined acceptance, work-item closure, release/deployment, or external evidence remains; a verified WP does not move the parent to `done`;
   - move to `done` only after every required WP and the combined plan-level criteria satisfy the `plan-spec` completion rule, with any Owner-approved exception recorded explicitly;
   - If Owner approval includes a test report without exact commands or scope, record it as Owner-reported, not as independently rerun/passed. For every unmet criterion, distinguish verified evidence, an explicit local-closure exception, and external acceptance still outstanding. A general “tested/approve done” must not imply Jira, role, live catalog, release, or deployment acceptance.
   - move to `discarded` only after the Owner or Prompter confirms abandonment of the plan, with reason and replacement link. Do not move individual WP files.
6. Update canonical `status`, `updated`, Execution scope when present, `Dispatch Log`, `Outcome`, append-only `History`, and the single README index entry in the same edit. Before and after a lifecycle move, scan `$PLAN_ROOT` Markdown for incoming links to the bundle slug; retarget only live link destinations, preserve historical quoted paths, and validate that changed relative links resolve and none still point to the old lifecycle. Update `updated` and append a path-only `History` entry in any affected canonical plan. Preserve the complete bundle and prior evidence.
7. Report inaccessible sources and ask one focused question only when the result depends on the Owner's acceptance. Do not commit.

## Next Command

Finish with one `Next:` line:

- Still in `open/`, remaining WP needs preparation/approval: `Next: /plan-write <slug> wp-N` after its dependency gates pass.
- Still in `open/`, a remaining WP is already approved and ready: `Next: /plan-dispatch <slug> wp-N` only when its dependency and isolation gates pass; do not launch it automatically.
- Still in `open/`, acceptance or external evidence pending: name the wait and `Next: /plan-sync <slug>` after it lands.
- Moved to `done/` or `discarded/`: `Next: /plan-retro` when a batch has finished.

## Commands

Run these only after the `PLAN_ROOT` gate passes.

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
find "$PLAN_ROOT/open" -mindepth 2 -maxdepth 2 -type f -name '*.md' -print | sort
git -C <repo> log --oneline --decorate <base>..<branch>
git -C <repo> diff --stat <base>...<branch>
git -C <repo> diff --check <base>...<branch>
<issue-tracker-status-command>
<code-host-review-status-command>
<ci-status-command>
mv "$PLAN_ROOT/open/<plan-slug>" "$PLAN_ROOT/done/<plan-slug>"
mv "$PLAN_ROOT/open/<plan-slug>" "$PLAN_ROOT/discarded/<plan-slug>"
```

Use the configured source-host integration to read review files, reviews, comments, and check runs as needed.

## Remote State

Never merge a review, approve your own work, close or transition an external work item, add a release marker, or trigger deployment merely to make the plan appear complete. Show the exact remote action that remains and let the Owner or recorded owner perform it unless the current request explicitly authorizes that mutation.