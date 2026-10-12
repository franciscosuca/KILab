---
name: plan-status
description: "Report plan status across drafts, next, open, done, and discarded, including readiness, review, CI, release, and person-versus-system blockers."
argument-hint: "[plan slug or ticket key, optional full; omit for all plans]"
user-invocable: true
---

# Report Plan Status

Read the sibling `plan-spec/SKILL.md` first. Before inventorying or reading lifecycle data, pass its `PLAN_ROOT` fail-closed gate. If no valid absolute root is available, ask the user for it and stop; do not scan a guessed location. This skill is read-only: do not move plans, edit the index, transition tickets, approve PRs, or queue pipelines.

## Quick Status

Use this when the request names one plan, such as `/plan-status iiot-2789`. Report only that plan, from local files; do not call remote systems. Include review, CI, or external work-item state only when the request adds `full`, and then use the batch checks for that plan.

Run this snippet with the plan name in `SLUG`:

```bash
SLUG='<plan-slug-or-ticket-key>'
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
MATCHES=$(find "$PLAN_ROOT" -mindepth 2 -maxdepth 2 -type d \( -name "$SLUG" -o -name "$SLUG-*" \) | sort)
COUNT=$(printf '%s\n' "$MATCHES" | grep -c '/' || true)
if [ "$COUNT" -eq 0 ]; then
  printf 'No bundle matches %s; check the slug, or run /plan-status without a slug.\n' "$SLUG"
  exit 3
fi
if [ "$COUNT" -gt 1 ]; then
  printf '%s bundles match %s; list them and ask which one.\n%s\n' "$COUNT" "$SLUG" "$MATCHES"
  exit 3
fi
BUNDLE=$MATCHES
NAME=$(basename "$BUNDLE")
CANON="$BUNDLE/$NAME.md"
printf 'bundle: %s\nfolder: %s\n' "$BUNDLE" "$(basename "$(dirname "$BUNDLE")")"
awk 'NR==1 && /^---$/ {f=1; next} f && /^---$/ {exit} f' "$CANON" | grep -E '^(status|created|updated|blocked_by):'
printf 'request: %s\n' "$(test -f "$BUNDLE/context/request.md" && echo yes || echo no)"
printf 'work-packages: %s\nworkflows: %s\n' "$(find "$BUNDLE/work-packages" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')" "$(find "$BUNDLE/workflows" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo 'history:'
awk '/^## History/ {f=1; next} /^## / {f=0} f && /^- /' "$CANON"
echo 'execution scope:'
awk '/^## Execution scope/ {f=1; print; next} /^## / {f=0} f' "$CANON"
echo 'dispatch and outcome:'
awk '/^## (Dispatch Log|Outcome)/ {f=1; print; next} /^## / {f=0} f' "$CANON" | head -20
```

Report four lines:

1. `<bundle name> · <folder>/ · status <status> · updated <date>`, plus execution mode, selected/next WP, and per-WP progress counts when recorded. Do not equate WP file counts with completed WPs.
2. `Commands run:` the History lines as `date command: result`. Without a History section, write `not recorded; inferred from files:` and list what the files show: `context/request.md` means plan-add ran; `updated` later than `created` means plan-write or a later command ran; a Dispatch Log means plan-dispatch ran; an Outcome means plan-sync ran.
3. `Flags:` lifecycle/status mismatches, canonical or selected-WP blockers, missing scope/approval records, duplicate active writers, or contradictory WP evidence. Existing supporting files alone do not prove approval; flag missing approval/request evidence rather than inferring an unauthorized transition. In a WP-mode plan, distinguish deferred WP-specific gates from blockers on the next slice. Write `none` when there are none.
4. `Next:` one command from `## Next Command`, using this plan's folder and blockers.

If the snippet finds no match or several matches, show the matches and stop. Do not guess.

## Procedure

1. Inventory every lifecycle folder as plan bundles plus unclassified legacy plans. Report one canonical plan per bundle and do not report context, workflow, or work-package files as separate plans.
2. Validate that each canonical file's frontmatter `status` matches its bundle's lifecycle folder. Report mismatches first.
3. For drafts, identify the unanswered decision or missing evidence and whether the whole plan or first bounded WP can now be approved. Empty supporting folders are expected and are not blockers.
4. For next plans, report execution mode, selected WP when scoped, approval/dependency readiness, excluded scope, and the exact next action. Never recommend an unscoped dispatch for a WP-mode plan.
5. For open plans, read every recorded review, policy, check run, external work item, and promised release or deployment. Reconcile those records with Execution scope and Dispatch Log per WP; distinguish local implementation, review-pending work, and verified WPs. Report remaining planned/ready/blocked WPs in the parent's single line, not as independent plans. Compare all remaining work and plan-level gates to the done criteria; one finished WP is not a finished plan.
6. Classify waits as:
   - `person`: approval, answer, access grant, or ticket-owner action;
   - `decision`: unresolved product or architecture choice;
   - `system`: CI, release, credentials, environment, upstream service, or deployment;
   - `implementation`: agent work or failed verification still in progress.
7. Mark a plan stale only when it has no recorded activity for 14 days and no explicit wait. State inaccessible sources as `unverified`, not failed or clear.

## Next Command

Give each plan one next command, using the first matching row:

| Folder and state | Next command |
|---|---|
| `drafts/`, selected scope needs decisions, evidence, or approval | Name the gate; then `/plan-write <slug> wp-N` when scoped, otherwise `/plan-write <slug>` |
| `drafts/`, selected scope ready | Owner approves; `/plan-write <slug> wp-N` when scoped, otherwise `/plan-write <slug>`, moves it to `next/` |
| `next/` or `open/`, selected scope has unresolved blockers/dependencies | Name the gate and its owner; no dispatch yet |
| `next/`, whole-plan execution ready | `/plan-dispatch <slug>` |
| `next/` or `open/`, a WP is approved and ready with safe isolation | `/plan-dispatch <slug> wp-N` |
| `open/`, active scope still implementing or waiting on review/CI/release | Name the wait; `/plan-status <slug>` again when it changes |
| `open/`, a WP has acceptance evidence awaiting verification | `/plan-sync <slug>`; do not call it verified from local results alone |
| `open/`, remaining WP needs preparation/approval after prior gates pass | `/plan-write <slug> wp-N` |
| `open/`, all required scope and evidence ready for whole-plan verification | `/plan-sync <slug>` |
| `done/`, `discarded/` | `/plan-retro` when reviewing a batch |
| Legacy, unclassified | Ask the Prompter before classifying; no command |

End the report with one `Next:` line for the most urgent plan. If a recorded WP selector is missing or ambiguous, ask which WP rather than inventing one. A review-pending predecessor blocks its dependent WP unless explicit parallel-safe approval is recorded; an independent ready WP can be suggested only when dispatch isolation passes. These are suggestions; this skill never runs them.

## Commands

Run these only after the `PLAN_ROOT` gate passes.

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
find "$PLAN_ROOT" -mindepth 2 -maxdepth 3 -type f -name '*.md' -print | sort
grep -RniE '^(status:|updated:|blocked_by:|pull_requests:|depends_on:)' "$PLAN_ROOT" 2>/dev/null
git -C <repo> status --short --branch
git -C <repo> log -1 --date=iso-strict --format='%ad %h %s' <branch>
<issue-tracker-status-command>
<code-host-review-status-command>
<ci-status-command>
```

Use the configured source-host and CI integrations to read review and check state. A missing login or unavailable connector is an access gap; do not initiate interactive authentication during a status report.

## Report Format

Return these sections, omitting empty ones: `Needs attention`, `Ready to write`, `Ready to dispatch`, `In progress`, `Waiting on people`, `Waiting on decisions`, `Waiting on systems`, `Recently done`, and `Unclassified legacy`. Each plan gets one compact line with ticket/title, age, owner, PR, current evidence, and next command from `## Next Command`.