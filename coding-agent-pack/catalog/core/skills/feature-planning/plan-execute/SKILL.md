---
name: plan-execute
description: "Implement exactly one approved feature-planning v2 plan, or resume its recorded checkpoint, with safe worktree ownership, exact checks, and durable receipts. Never self-merge or declare completion."
argument-hint: "<plan slug or unambiguous issue key>"
user-invocable: true
---

# Execute An Approved Plan

Read the [shared contract](../plan-spec/SKILL.md) first. Pass its absolute `PLAN_ROOT` gate before selecting/reading plans or changing code. Require one explicit, unambiguous **v2** plan from next, or open for a deliberate resume. No automatic queue selection, legacy execution, extra unit selector, or terminal-plan redispatch. On a failed gate, stop with an explicit conditional `Next:` command.

## Preflight — Before State Or Code Changes

1. Read metadata, agent contract, relevant artifacts and prior receipts. Require current scope approval (`approved_revision == scope_revision`), attributable approval evidence, exact repository/file boundaries, non-goals, inline steps/acceptance, branch/base, executable verification commands and stop conditions. Run the contract validator with `--ready`; this checks declared structure, not actual consent.
2. Inspect current code/base and dependencies; require verified prerequisites or explicit parallel-safe approval with non-overlapping ownership/base assumptions. No execution blockers may be hidden as later acceptance. Stop for changed scope, stale approval, incomplete readiness or unknown publication permissions; recommend plan-create to resolve them.
3. Inspect target repository/worktree status, active writers/run IDs, existing branches/reviews and partial changes. Preserve unrelated edits/stashes/worktrees; stop for overlapping user changes, duplicate writers or unclear ownership. Never reset/delete/force-push to manufacture isolation.
4. For an open resume, inspect the last checkpoint, partial diff/commits and receipts before doing anything. If a writer is still active, do not start another: recommend plan-sync after its evidence is available. Reuse authorized work and completed steps; rerun only checks invalidated by changed code/base/environment, documenting why. A connection failure is not permission to replay completed stages or change providers/models.
5. Verify tools/access needed for this implementation. Direct execution is supported; delegation is optional and requires operator/project authorization plus available harness support. Do not require an extension, invent an agent tool, or widen a delegated boundary. Record unavailable evidence; stop when access is required for execution.

## Execution And Handoff

1. When implementation actually starts, move the complete next bundle to open once, repairing authorized live links/index. An open resume stays open. Record active writer/run (or direct agent), approved revision, branch/base, timestamp and initial checkpoint before edits; update both views and append History.
2. Implement only the approved inline steps. Follow repository abstractions, package manager, lockfile and contribution policy. Validate after focused edits and repairs. An unexpected prerequisite or necessary change outside scope is a stop-and-ask condition, not authority to extend the plan or start another plan.
3. Keep one writer per owned surface. If authorized delegation is used, pass the exact canonical path after moves, repository/worktree, revision/boundary, dependencies, checks, non-goals, stop conditions and dirty-file warnings. Record the run ID; launch/completion receipts alone are not acceptance. Consume results before recording handoff.
4. Record focused/regression commands and actual results, tested commit/tree, artifacts, remaining steps, failures/deviations and partial branch/diff state. Leave failures open at a recoverable checkpoint; do not silently rewind lifecycle or discard work.
5. Publication is local-only unless the current request or recorded permissions explicitly authorize commits/push/draft review. When authorized: review the diff, stage only in-scope files, use repository commit/sign-off policy, push without force, and create the approved draft review against the recorded base. Include Problem, Changes, exact Verification and Dependencies/rollout. Preserve external IDs and real reviewer ownership; never invent formal review or self-merge. No tracker transition/release/deployment is implicit.
6. Before handoff, reread plan/index for concurrent edits, clear only completed active-writer ownership, update current resume/checkpoint, exact receipts/artifact links, both views (per-delivery commit links where available), updated date, History and one index entry. Keep the bundle open. Do not label delivery or a green local run whole-plan verification.

## Result And Next Command

Report implementation versus acceptance status, exact checks, publication receipts/permissions, checkpoint/blocker and remaining work. Every result—including failed, blocked, unchanged, checkpoint and handoff—must end with one `Next:` line.

- Handoff/active run/evidence pending: `Next: /plan-sync <actual-slug> — once <named evidence> is available.`
- Paused, approved work remains, no active writer: `Next: /plan-execute <actual-slug> — after <resume gate>.`
- Scope/approval/readiness changed: `Next: /plan-create <actual-slug> — resolve <named gate> and approve the revised contract.`

Align TL;DR/Resume Next on mutations. Never auto-run the recommendation or start another plan.
