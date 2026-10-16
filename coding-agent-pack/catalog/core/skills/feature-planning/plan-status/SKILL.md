---
name: plan-status
description: "Optional read-only inspection of v2 and legacy plan state, approval/readiness, recorded evidence and named blockers. Always recommend a next primary command; never modify plan data."
argument-hint: "[plan slug or issue key] [full]"
user-invocable: true
---

# Inspect Plans — Read-only

Read the [shared contract](../plan-spec/SKILL.md) first. Pass its absolute `PLAN_ROOT` gate before inventorying or reading plan data. Ask and stop if missing/invalid. Do not initialize, repair, migrate, edit the index/views/history, move plans, approve scope, launch writers, commit, authenticate interactively, or mutate any remote system.

## Procedure

1. Resolve one requested bundle, asking on ambiguity; without a selector, inventory canonical v2 bundles plus clearly labeled legacy plans. Supporting artifacts are never plans. Do not infer a missing identifier or pick a queued plan for execution.
2. For a named plan, default to local recorded information only. With `full`, use available read-only remote integrations for review/CI/issue/release evidence relevant to that plan. Label observation times, old receipts and inaccessible sources accurately. No login attempt or failure-as-success inference.
3. Report lifecycle/status mismatches first, then approval revision/evidence, dependencies/blockers, current checkpoint/active writer, completed/remaining inline steps and last recorded history. A file's existence or date does not prove which command ran or that work was approved/tested. Legacy approval/commands are unverified unless actually recorded.
4. Separate waits on a person, decision, system or implementation; name owner/service. A merged review, local pass, contributor check or worker completion is not full acceptance. Show current local-closure exceptions and outstanding external acceptance separately. Flag duplicate writers and stale approval; never suggest resuming over an active writer.
5. The contract's validator can inspect structure/index/links read-only. Report failures; do not fix them. Mark legacy content as requiring explicit migration before v2 mutation. Treat no activity for 14 days as stale only when no explicit wait is recorded.

## Result And Next Command

Use one compact line per plan: slug/title, lifecycle/date, revision/approval, implementation versus acceptance, named blocker and suggested primary command. Omit empty report categories. For multiple plans, finish with the most urgent justified next action without choosing it for execution.

Every result—including failed, blocked, unchanged, checkpoint and handoff—must end with one `Next:` line from the shared contract, using actual resolved arguments and readiness conditions. Prefer plan-create for missing approval/scope, plan-execute only for ready paused work with no writer, plan-sync for running/pending evidence, and plan-retro for terminal plans. Unknown targets use explicitly labeled placeholders plus a focused question. Nothing is automatically run or rewritten.
