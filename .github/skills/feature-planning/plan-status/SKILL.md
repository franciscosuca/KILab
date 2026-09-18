---
name: plan-status
description: "Report plan status across drafts, next, open, done, and discarded, including readiness, review, CI, release, and person-versus-system blockers."
argument-hint: "[area, ticket key, or lifecycle state]"
user-invocable: true
---

# Report Plan Status

Read `.github/skills/plan-spec/SKILL.md` first. This skill is read-only: do not move plans, edit the index, transition tickets, approve PRs, or queue pipelines.

## Procedure

1. Inventory every lifecycle folder plus unclassified legacy plans.
2. Validate that each plan's frontmatter `status` matches its folder. Report mismatches first.
3. For drafts, identify the unanswered decision or missing evidence and whether it can now be written.
4. For next plans, report dependency readiness and the exact next action.
5. For open plans, read every recorded review, policy, check run, external work item, and promised release or deployment. Compare status to the plan's done criteria.
6. Classify waits as:
   - `person`: approval, answer, access grant, or ticket-owner action;
   - `decision`: unresolved product or architecture choice;
   - `system`: CI, release, credentials, environment, upstream service, or deployment;
   - `implementation`: agent work or failed verification still in progress.
7. Mark a plan stale only when it has no recorded activity for 14 days and no explicit wait. State inaccessible sources as `unverified`, not failed or clear.

## Commands

```bash
PLAN_ROOT="${PLAN_ROOT:-research/plans}"
find "$PLAN_ROOT" -maxdepth 2 -type f -name '*.md' -print | sort
grep -RniE '^(status:|updated:|blocked_by:|pull_requests:|depends_on:)' "$PLAN_ROOT" 2>/dev/null
git -C <repo> status --short --branch
git -C <repo> log -1 --date=iso-strict --format='%ad %h %s' <branch>
<issue-tracker-status-command>
<code-host-review-status-command>
<ci-status-command>
```

Use the configured source-host and CI integrations to read review and check state. A missing login or unavailable connector is an access gap; do not initiate interactive authentication during a status report.

## Report Format

Return these sections, omitting empty ones: `Needs attention`, `Ready to write`, `Ready to dispatch`, `In progress`, `Waiting on people`, `Waiting on decisions`, `Waiting on systems`, `Recently done`, and `Unclassified legacy`. Each plan gets one compact line with ticket/title, age, owner, PR, current evidence, and next action.