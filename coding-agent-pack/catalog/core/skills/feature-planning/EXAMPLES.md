# Feature-planning v2 Examples

See [README.md](README.md) for the primary lifecycle. All paths/commands below are examples, not records of implementation or test execution. Supply an actual absolute `PLAN_ROOT`; never copy a placeholder as a real environment setting.

## 1. Create And Investigate

```text
/plan-create

Request: validate configuration before saving.
Constraints: preserve compatible error responses; no unrelated cleanup.
No issue number was supplied. Use XXXX, not an invented number.
Preserve this request in artifacts/request.md. Inspect owning code, tests,
configuration and history. Write both views; do not implement or publish.
Keep the plan in drafts until the current revision is approved and ready.
```

Expected recommendation while approval is missing:

```text
Next: /plan-create plan-XXXX-config-validation — after Owner approval of scope revision 1 and resolution of readiness gaps.
```

To record approval after reviewing the actual implementation contract:

```text
/plan-create plan-XXXX-config-validation

Approve scope revision 1 exactly as written. Record this approval.
Move the complete bundle to next only if all execution gates pass.
Do not implement yet. Publication remains local-only.
```

## 2. Execute Or Resume

```text
/plan-execute plan-XXXX-config-validation

Implement the approved inline steps only. Verify approval/dependencies,
branch/base and safe worktree ownership first. Resume a paused checkpoint
without replaying completed work or starting a duplicate writer.
Run the exact checks, record actual results and keep acceptance unverified
until synchronization. No commit/push/review without separate permission.
```

Expected handoff recommendation:

```text
Next: /plan-sync plan-XXXX-config-validation — reconcile implementation receipts and the required review/check evidence.
```

## 3. Synchronize

```text
/plan-sync plan-XXXX-config-validation

Compare every required acceptance criterion with implementation, tested
and landed trees, review/check evidence, and any promised external gates.
Refresh both views and commit-link each delivered statement when possible.
Keep open if evidence is missing. Record Owner-reported tests and exact
exceptions without inventing CI, tracker, role or deployment acceptance.
Repair authorized live links/index if moving the complete bundle.
```

Expected recommendation only after verified/explicitly excepted completion:

```text
Next: /plan-retro plan-XXXX-config-validation — review the completed outcome.
```

## 4. Retrospect

```text
/plan-retro plan-XXXX-config-validation

Review corrections, execution evidence, reviews and failures. Record concise
plan findings. Propose the smallest evidence-backed skill edits and wait
for explicit approval before applying them. Do not commit or redispatch.
```

If changes are proposed:

```text
Next: /plan-retro plan-XXXX-config-validation — after explicit approval of the proposed edits.
```

If the retro is complete with nothing remaining:

```text
Next: /plan-create <new-request> — only when another task exists; new-request is a placeholder.
```

## Complete Illustrative Draft

This fictional intake demonstrates the file format, not implementation readiness. Dates are example values; code paths/commands must be investigated before approval. Nothing has been delivered, so no commit link is fabricated. Copy to `drafts/plan-XXXX-config-validation/plan.md` only in an explicitly selected sandbox; also preserve the actual request in `artifacts/request.md` and its unique root index entry.

```markdown
---
schema_version: 2
id: null
title: "Validate configuration before saving"
status: "draft"
owner: "Owner"
created: "2026-01-01"
updated: "2026-01-01"
sources: []
repositories: []
branches: []
pull_requests: []
depends_on: []
blocked_by: ["Owner: scope approval and controlling code/test discovery pending"]
scope_revision: 1
approved_revision: null
approved_by: null
approved_at: null
---
# Validate configuration before saving

## tldr-version

**Scope:** Reject invalid configuration before persistence; preserve compatible errors and valid saves.

**Status:** Draft; owning code/tests, verification commands and scope approval remain unresolved.

**Delivered:** None yet.

**Next:** `/plan-create plan-XXXX-config-validation` — investigate the controlling path and request approval of revision 1.

## agent-version

### Resume
- Completed: request captured; no implementation.
- Remaining: controlling code/test discovery, exact checks, approval.
- Active writer: none.
- Next: /plan-create plan-XXXX-config-validation — investigate and obtain revision 1 approval.

### Scope
- Goal: reject invalid input before persistence without unrelated changes.
- Non-goals: new storage, authentication redesign, adjacent cleanup.
- Compatibility: characterize existing error and valid-save behavior first.
- Approval evidence: none; do not set approved_revision yet.
- Publication: local-only; no commit/push/review permission.
- Request: [original input](artifacts/request.md).

### Implementation
1. Planned: inspect owning repository instructions, save/validation symbols
   and nearest negative-path test. Record exact files, dependencies and checks.
2. Planned: implement approved validation at the smallest controlling boundary.
   Acceptance: invalid input has no persistence effect; valid saves remain compatible.
3. Planned: add focused/regression tests and current documentation where needed.
   Acceptance: exact named checks pass on the delivered tree.

### Verification
- Working directory and exact commands: unresolved; investigation required.
- Required cases: invalid/malformed input, authorization order, no partial
  writes, compatible errors and unchanged valid saves.
- No tests, review, CI, release, device or deployment acceptance claimed.

### History
- 2026-01-01 /plan-create plan-XXXX-config-validation: illustrative intake; request preserved.
```

## Delivered Statements And Diagram

Once actual delivery exists, replace `None yet.` with one bullet per statement. Each gets its own authoritative commit link, even when several statements share a commit. For example, use `[short SHA](actual source-host commit URL)` populated from real receipts; do not turn this illustrative placeholder into a delivery claim. For verified uncommitted work explicitly say `uncommitted`; genuinely unavailable commit evidence is `commit unavailable`.

An optional `**Diagram:**` field follows Next and contains one fenced Mermaid block supported by the current plan. Do not add separate Evidence/Limits/Steps fields to the TL;DR. Important closure limits fit Status; details belong in the agent view.
