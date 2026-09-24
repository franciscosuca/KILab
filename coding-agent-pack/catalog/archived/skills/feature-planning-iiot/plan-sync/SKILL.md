---
name: plan-sync
description: "Synchronize open plans with reviews, CI, external work items, releases, and deployments; move only verified work to done and confirmed abandoned work to discarded."
argument-hint: "[plan name or ticket key]"
user-invocable: true
---

# Synchronize Plans

Read `.github/skills/plan-spec/SKILL.md` first. Synchronization compares recorded intent with what actually landed. A merged PR alone is not always done.

## Procedure

1. Resolve `PLAN_ROOT` and select the requested canonical plan or every plan bundle in `$PLAN_ROOT/open/`. Do not treat supporting files as separate plans.
2. Read the canonical plan's acceptance criteria, verification commands, dependencies, PRs, and promised release or deployment. Read related work packages and workflows as supporting scope.
3. Check each review's state, latest commit, unresolved comments, required policies/checks, and merge result. Check the linked external work item and release evidence such as a release marker, release-system record, deployed version, or documented smoke test when the plan requires it.
4. Compare changed files and reported results with every plan phase. Record omitted, added, or changed scope in `Outcome`; do not silently rewrite the original plan to match the PR.
5. Apply one result:
   - keep in `open` when implementation, review, CI, work-item closure, release, deployment, or external verification remains;
   - move to `done` only when the `plan-spec` completion rule passes;
   - move to `discarded` only after the Owner or Prompter confirms abandonment, with reason and replacement link.
6. Update canonical `status`, `updated`, `Dispatch Log`, `Outcome`, and the README index in the same edit. Preserve the complete bundle.
7. Report inaccessible sources and ask one focused question only when the result depends on the Owner's acceptance. Do not commit.

## Commands

```bash
PLAN_ROOT="${PLAN_ROOT:?Set PLAN_ROOT to the configured planning root}"
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