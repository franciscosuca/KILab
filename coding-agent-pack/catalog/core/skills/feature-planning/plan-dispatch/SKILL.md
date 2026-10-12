---
name: plan-dispatch
description: "Dispatch an implementation-ready plan or one approved work package to an isolated coding agent, track its branch and checks, and open a draft review for the Owner. Never merge the change."
argument-hint: "<plan name or ticket key> [wp-N]"
user-invocable: true
---

# Dispatch A Plan

Read the sibling `plan-spec/SKILL.md` first. Before selecting a plan or launching implementation, pass its `PLAN_ROOT` fail-closed gate. If no valid absolute root is available, ask the user for it and stop without dispatching or changing any plan. `/plan-dispatch` authorizes implementation, commits, push, and a draft review only for the selected scope, but never authorizes merging, external work-item transitions, discarding work, or automatically starting another WP.

## Scope Selection

- `/plan-dispatch <slug>` dispatches the whole plan from `next` only when no active work-package boundary is recorded (a legacy plan without Execution scope, or an explicitly approved `Mode: whole-plan`).
- `/plan-dispatch <slug> wp-N` dispatches exactly one approved, ready WP from `next`, or continues the same canonical plan from `open`.
- Resolve the plan name/ticket to one canonical bundle, and the selector to one WP under the `plan-spec` contract. Do not interpret `<ticket>-wp1` as a new plan, guess a missing WP, or select a work-package file as the lifecycle owner.
- If the plan records work-package execution but the selector is omitted, ask which WP to run. If scope/approval/readiness is missing, stop and suggest `/plan-write <slug> wp-N`; do not silently widen the work. Returning to whole-plan execution requires explicit approval.

## Preflight

1. Resolve and validate `PLAN_ROOT` before any lifecycle scan. Then select exactly one canonical plan from `next`, or from `open` only for an explicit WP continuation. When no plan name is supplied, choose the first unblocked `next` bundle in the index and state the choice; never choose an open continuation automatically. A draft is not dispatchable.
2. Read the canonical plan, relevant context, and prior Dispatch Log/Outcome; when scoped, also read the selected WP definition and Execution scope. Confirm approval for the selected scope and a `ready` row when scoped, exact in-scope files/shared changes, excluded WPs, acceptance criteria, runnable checks, repositories, and branch/base. Canonical blockers must be empty; canonical dependencies and any selected-WP dependencies must be verified/done or explicitly parallel-safe. Later WP-specific blockers do not block an independent slice, but shared blockers always do.
3. Reject a duplicate `in-progress` or `in-review` WP, or a `verified` WP unless an explicit repair/rework request reopens its scope. Inspect every target worktree and existing review branch. Preserve unrelated changes; stop for overlapping user changes, another active writer, unresolved predecessor gates, or unclear isolation/base assumptions. Do not auto-dispatch prerequisites.
4. Confirm access to each required external system and that an available subagent tool can launch the bounded worker before changing lifecycle state. If delegation is unavailable, stop without moving the bundle or falling back to direct implementation. Record unavailable external connections as unverified; stop when one is necessary for this dispatch.
5. For the first dispatch only, change canonical status to `open` and move the complete bundle from `next` to `$PLAN_ROOT/open/<plan-slug>/`. A continuation is already `open` and stays there. For scoped work, mark only the selected WP `in-progress`; whole-plan execution does not require a WP table. Record scope/WP when applicable, timestamp, agent, branch/base, and checks in `Dispatch Log`, append a History line including the WP selector when scoped, set `updated`, and refresh the single index entry before launching work.

## Agent Contract

Launch an isolated implementation agent with the available subagent tool (`subagent` from pi-subagents in Pi, or your harness's equivalent). Pass the canonical path after any move, bundle path, selected WP when scoped and its existing supporting path when present, resolved implementation boundary, target repository/worktree, branch/base, dependencies, exact checks, acceptance/stop criteria, non-goals, excluded WPs, and dirty-file warnings. The instruction is: implement only the authorized scope, treat other phases/WPs as context, validate after each focused edit, record deviations, and never merge. A necessary change outside the approved boundary is a stop-and-ask condition, not permission to implement another WP.

If the harness returns a background run ID, record it and keep the selected WP `in-progress` while the worker runs. Use the harness's supported status/completion mechanism; a successful launch receipt is not implementation or acceptance evidence. Apply the Handoff steps only after the implementation results and checks are available.

Use the branch/base recorded for this dispatch. Do not reuse another WP's branch or draft review merely because it belongs to the same ticket. Follow the target repository branch pattern; the fallback is `<type>/<ticket-lower>-<slug>` or `<type>/<slug>`, adding `-wp-N` for a scoped branch, where type is `feat`, `fix`, `docs`, `refactor`, `test`, `build`, or `ci`. Record any deliberate shared or stacked branch arrangement and its base/ownership before launch. Never reset, delete, or force-push an existing branch to isolate work.

Commits use the repository's required format; when none is documented, use `type(scope): outcome`. Apply sign-off or other repository policy when required. Review titles preserve the external identifier and source summary when available; otherwise use the commit form. The body contains `Problem`, `Changes`, `Verification`, and `Dependencies / rollout`, with exact command results.

## Next Command

Finish with `Next: /plan-status <slug>` to follow the selected scope's draft review and checks. Suggest `/plan-sync <slug>` once its evidence is ready. Do not launch the next WP; the bundle stays in `open/` until whole-plan completion is verified.

## Commands

Run these only after the `PLAN_ROOT` gate passes.

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
git -C <repo> status --short --branch
git -C <repo> branch --show-current
git -C <repo> remote -v
git -C <repo> switch -c <branch>
git -C <repo> diff --check
git -C <repo> diff --stat
# Use next for a first dispatch, open for an explicit WP continuation.
find "$PLAN_ROOT/<current-lifecycle>/<plan-slug>" -maxdepth 3 -type f -print | sort
git -C <repo> commit -m '<type>(<scope>): <outcome>'
git -C <repo> push -u origin <branch>
<code-host-create-draft-review-command>
```

Run the selected scope's exact verification commands and required shared regression checks before commit and again after any repair. Review the diff and stage only authorized files; refuse unexplained changes from other WPs. Use the source host's supported integration to create a scope-specific draft review and request the recorded Owner or reviewers. Include the WP identifier and remaining excluded scope in a scoped review title/body.

## Handoff

Append the scope/WP when applicable, agent/run ID, branch/base, commit SHAs, draft review URL, exact command results, CI/review state, deviations, and blockers to the canonical `Dispatch Log`; refresh `updated` and the index, and append a handoff History line without rewriting earlier entries. Mark a successfully handed-off WP `in-review`, not `verified`. If launch or implementation fails, record the precise failure and partial branch/diff state, mark the selected WP `blocked` (or canonical `blocked_by` for whole-plan work), and keep the bundle `open`; do not move it backward or switch execution mode without approval. Stop after the authorized scope's handoff. Only `/plan-sync` verifies WP evidence and decides whether the whole plan is done.