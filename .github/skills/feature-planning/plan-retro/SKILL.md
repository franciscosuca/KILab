---
name: plan-retro
description: "Review completed and discarded plans, review feedback, CI failures, commits, and agent corrections to propose evidence-based improvements to the plan skills."
argument-hint: "[date range, area, or plan names]"
user-invocable: true
---

# Retrospect On Plans

Read `.github/skills/plan-spec/SKILL.md` first. The retro improves the workflow from observed repetition. It proposes skill edits; it does not apply or commit them until the Prompter approves.

## Procedure

1. Default to plans moved to `done` or `discarded` in the last 90 days. Include their `Dispatch Log`, `Outcome`, linked reviews, checks, external work items, and releases.
2. Query local agent sessions for corrections, retries, requests for exact commands, and cases where a proposal was not applied. Search external conversation only when an authorized connector exists.
3. Inspect recent commits and PR follow-ups around the same topic. Distinguish a repeated workflow defect from one product-specific bug.
4. Require at least two independent examples before proposing a durable rule. One severe data-loss, security, or credential event may justify a rule immediately.
5. Look especially for repeated patterns: wrong package manager or working directory, release-runner failure, missing credentials or configuration, untested pipeline or container entrypoint, stale external/local diagrams, excessive scope or wording, runtime mock data after real integration, and agents stopping at suggestions.
6. For each finding, name the evidence, why the current skill allowed it, the smallest exact edit, and the check that would prove the edit helps. Also identify obsolete or duplicate rules.
7. Present the proposed diffs grouped by skill and wait for approval. After approval, edit only the accepted skills and run their structural checks. Never commit.

## Commands

```bash
PLAN_ROOT="${PLAN_ROOT:-research/plans}"
find "$PLAN_ROOT"/{done,discarded} -maxdepth 1 -type f -name '*.md' -mtime -90 -print | sort
git -C <repo> log --all --since='90 days ago' --date=short --format='%ad %h %s%n%b'
git -C <repo> log --all --since='90 days ago' --grep='fix\|revert\|follow-up\|pipeline\|deploy' -i --oneline
grep -RniE 'failed|blocked|deviation|follow-up|retry|unverified' "$PLAN_ROOT"/{done,discarded} 2>/dev/null
wc -l -w .github/skills/plan-*/SKILL.md
```

Use the available local session-history tool with a bounded query, adding repository or topic filters when possible. Use the configured source-host, issue-tracker, CI, release, and deployment integrations to collect remote evidence. Record every unavailable source.

## Output

Return: date range and sources reached; repeated pattern; two or more examples; affected skill; proposed replacement text; expected benefit; and a cheap validation. State explicitly when an external tracker, source host, documentation system, chat connector, CI, release, or deployment source could not be reached.