---
name: plan-retro
description: "Review completed/discarded plans and observed corrections to propose small evidence-backed planning improvements; apply only explicitly approved edits, never redispatch completed work."
argument-hint: "<plan names, date range, or area>"
user-invocable: true
---

# Learn From Completed Plans

Read the [shared contract](../plan-spec/SKILL.md) first. Pass its absolute `PLAN_ROOT` gate before searching plan data/history. Missing root: ask and stop with a conditional `Next:` command. Retrospective findings do not reopen, execute, or move terminal plans.

## Procedure

1. Resolve the requested selection; otherwise inspect plans completed/discarded in the last 90 days using recorded closure/history dates, not artifacts as independent plans. Read canonical contracts, Outcome/Execution receipts, linked evidence, relevant review/check/commit follow-ups and available authorized session history. Legacy sources may inform findings read-only; do not convert them implicitly.
2. Mark unavailable external issue/docs/chat/host/CI/release/deployment/session sources explicitly. Compare actual evidence, corrections and retries; do not infer current remote state from historical notes.
3. Require two independent examples before a durable general rule. A severe security/credential/data-loss incident can justify a rule immediately. Separate recurring workflow failures from product-specific bugs.
4. Look for wrong working directory/package manager/lockfile, unsafe credential output, untested CI/container startup, stale docs/diagrams, missing identity/configuration, runtime mock data, overlong duplicated context, unclear approval/scope, replayed stages, missing commit links/next commands, broken lifecycle links and overstated local closure.
5. For each finding, give evidence links, why the current instruction allowed it, the smallest exact proposed edit/removal, expected benefit and a cheap validation. Keep product follow-ups separate from planning-rule changes.
6. For selected v2 terminal plans, record concise plan-specific findings under `### Retrospective` in the agent view; detailed evidence can live in artifacts, never a separate workflow/implementation plan. Preserve prior evidence/history and terminal status. Refresh current views/Next, updated date and index only where a finding is recorded; append History. Legacy plans remain unmodified.
7. Present proposed skill diffs and **wait for explicit approval**. Do not auto-edit skills just because a retrospective was requested. On a later authorized invocation, apply only the accepted edits to the named source collection, run structural tests/behavioral checks appropriate to the change, and record actual results. Never commit/push/publish implicitly.

## Result And Next Command

Return selection/date range, sources reached/unavailable, repeated pattern and examples, exact proposed edits, validation, and recorded plan findings. A no-findings result is valid; do not invent improvements or force a new task.

Every result—including failed, blocked, unchanged, checkpoint and handoff—must end with one explicit `Next:` line:

- Proposed edits await approval: `Next: /plan-retro <actual-selection> — after explicit approval of the proposed edits.`
- Approved validation/follow-up remains: `Next: /plan-retro <actual-selection> — after <named gate>.`
- Complete, no follow-up: `Next: /plan-create <new-request> — only when another task exists; new-request is a placeholder.`

Align TL;DR/Resume Next with this recommendation on v2 plan mutations, without inventing an actual new request. Never auto-run it or redispatch completed work.
