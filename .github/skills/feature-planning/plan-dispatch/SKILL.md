---
name: plan-dispatch
description: "Dispatch an implementation-ready plan to an isolated coding agent, track its branch and checks, and open a draft review for the Owner. Never merge the change."
argument-hint: "<plan name, ticket key, or next plan>"
user-invocable: true
---

# Dispatch A Plan

Read `.github/skills/plan-spec/SKILL.md` first. `/plan-dispatch` authorizes implementation, commits, push, and a draft review for the selected plan, but never authorizes merging, external work-item transitions, or discarding work.

## Preflight

1. Resolve `PLAN_ROOT` and select exactly one plan from `$PLAN_ROOT/next/`; when no name is supplied, choose the first unblocked entry in the index and state the choice.
2. Confirm `blocked_by` is empty, dependencies are done or explicitly parallel-safe, affected repositories and branches are named, and verification commands are exact.
3. Inspect every target worktree. If unrelated changes exist, preserve them. If user changes overlap planned files, stop and ask how to isolate the work.
4. Confirm access to each required external system. Record an unavailable issue tracker, source host, or CI connection instead of claiming it passed.
5. Change frontmatter to `open`, add the dispatch timestamp and agent to `Dispatch Log`, move the plan to `$PLAN_ROOT/open/`, and update the index before launching work.

## Agent Contract

Launch an isolated implementation agent with `runSubagent`. Pass the absolute plan path, target repository, branch, exact checks, non-goals, dirty-file warning, and this instruction: implement the plan, validate after each focused edit, record deviations, and never merge.

Use the branch already recorded in the plan. If none is recorded, follow the target repository pattern; the fallback is `<type>/<ticket-lower>-<slug>` or `<type>/<slug>`, where type is `feat`, `fix`, `docs`, `refactor`, `test`, `build`, or `ci`.

Commits use the repository's required format; when none is documented, use `type(scope): outcome`. Apply sign-off or other repository policy when required. Review titles preserve the external identifier and source summary when available; otherwise use the commit form. The body contains `Problem`, `Changes`, `Verification`, and `Dependencies / rollout`, with exact command results.

## Commands

```bash
PLAN_ROOT="${PLAN_ROOT:-research/plans}"
git -C <repo> status --short --branch
git -C <repo> branch --show-current
git -C <repo> remote -v
git -C <repo> switch -c <branch>
git -C <repo> diff --check
git -C <repo> diff --stat
git -C <repo> commit -m '<type>(<scope>): <outcome>'
git -C <repo> push -u origin <branch>
<code-host-create-draft-review-command>
```

Run the plan's verification commands before commit and again after any repair. Use the source host's supported integration to create a draft review and request the recorded Owner or reviewers.

## Handoff

Append branch, commit SHAs, draft review URL, command results, CI state, review state, deviations, and blockers to `Dispatch Log`. Keep the plan in `open`; only `/plan-sync` decides whether it is done.