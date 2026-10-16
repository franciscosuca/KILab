---
name: plan-sync
description: "Reconcile a v2 plan with actual implementation, commit/review/check evidence and explicit acceptance; refresh both views and move only verified or precisely excepted work to done."
argument-hint: "<plan slug or unambiguous issue key>"
user-invocable: true
---

# Synchronize Intent And Evidence

Read the [shared contract](../plan-spec/SKILL.md) first. Pass its absolute `PLAN_ROOT` gate before scanning/reading plans. Select one explicit v2 plan; ask on ambiguity. Legacy plans stay read-only pending authorized migration. This command reconciles evidence; it does not implement code, merge, approve its own work, transition external work items, release, deploy, or commit bookkeeping.

## Procedure

1. Read the current contract/revision/approval, dependencies, all required inline steps/acceptance, verification commands, resume/active-run information and prior receipts. Preserve original scope, historical results and remaining work.
2. Check actual changed files, tested commit/base/tree, published/merged content and relevant reviews/comments/required checks through available read-only integrations. Associate each receipt with its repository and exact tested tree; a test on another tree or a different repository does not verify this delivery. If landed content differs, identify invalidated checks. Do not falsely report a rerun.
3. Observe only the issue/release/deployment/operational evidence promised by this contract. Record unavailable connectors/access as unverified. A contributor/license check is not build/test CI; zero CI runs is not a queued or passing test job. A merged PR or completed agent run alone is not whole-plan completion.
4. Reconcile **every required** step and combined acceptance criterion. Retain unmet scope, regressions and changed assumptions; do not rewrite acceptance to match the diff. Missing commands/scope in an Owner test report remain Owner-reported, not independently tested. Distinguish verified evidence, explicit local-closure exceptions and external acceptance still outstanding. General “tested/approved” wording does not establish role grants, live catalog/device/cloud behavior, Jira closure or deployment acceptance.
5. Apply one evidence-backed result:
   - **Open:** required implementation, checks, reviews, decisions or external acceptance remain. Record named owner/type of wait and the real checkpoint. Do not start/restart a writer from this command.
   - **Done:** all required criteria in the shared completion rule are verified, or the Owner explicitly accepts an exact, plan-scoped exception for each unmet gate. Preserve residuals and local-versus-external limits; never inherit another plan's exception.
   - **Discarded:** Owner/Prompter explicitly confirms abandonment; record reason and replacement when known. No silent discard or partial-document move. Explicitly requested abandonment of a nonterminal draft/next plan follows the same confirmation rule.
6. Before edits/moves, reread for concurrent writers and inspect destination/incoming/outgoing live links/index. Move the complete bundle only; repair authorized live Markdown/reference/wiki destinations, not historical quoted/code paths. Obtain permission for legacy or other unauthorized edits before moving. In affected v2 canonical files, append path-only History/update dates without changing approval/scope. Preserve unrelated entries and evidence.
7. Update metadata, current Resume, Outcome/receipts, TL;DR's exact fields and per-delivered-claim commit links, updated date, append-only History and one lifecycle index entry. Validate layout, <300-word TL;DR, current index uniqueness, declared approval and changed local links with the shared validator. Do not auto-normalize unrelated legacy issues.

## Result And Next Command

Report what was verified, what was only reported, what was unavailable, exceptions/residuals, changed paths and resulting lifecycle. Ask a focused acceptance question if the decision depends on the Owner.

Every result—including failed, blocked, unchanged, checkpoint and handoff—must end with one `Next:` line:

- Active writer or acceptance/evidence pending: `Next: /plan-sync <actual-slug> — after <named evidence/action>.`
- Approved implementation remains, no active writer: `Next: /plan-execute <actual-slug> — after resume/readiness checks.`
- Revised scope/approval needed: `Next: /plan-create <actual-slug> — resolve <gate> and approve the changed revision.`
- Done/discarded: `Next: /plan-retro <actual-slug> — review the completed outcome.`

Keep stored TL;DR/Resume Next aligned on mutations. Recommendations do not authorize remote actions or auto-execution.
