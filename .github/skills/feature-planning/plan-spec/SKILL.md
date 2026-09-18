---
name: plan-spec
description: "Shared contract for repository plan folders, plan Markdown, lifecycle states, evidence sources, dependencies, and completion checks. Every plan-* skill must read this first."
user-invocable: false
---

# Plan Specification

Read this file before using any other `plan-*` skill. The plan file is the durable handoff between the Prompter, Owner, implementation agent, source control, CI, and any external systems named by the plan.

## Working Rules Learned From History

- Start with the user or system problem, then the desired workflow or result. Preserve screenshots, examples, current-versus-desired behavior, and explicit alternatives.
- Inspect the real implementation, schema, tests, and remote source before changing a plan or documentation. A local note or external page is context, not proof that behavior shipped.
- Keep wording short and technical. Preserve source terminology and external identifiers. Do not expand the scope to adjacent cleanup without naming it.
- When the Prompter says proceed, apply the approved change and validate it. Do not stop after repeating a proposal.
- Record every command that was run. A pipeline edit is not verified until its underlying build or test runs locally where possible and the real CI policy succeeds.
- Recheck package manager, lockfile, working directory, release runner, credentials, container startup command, and runtime environment. These commonly cause follow-up fixes.
- If documentation or a diagram mirrors an external source, compare both directions before calling it current. Do not replace editable diagrams with screenshots unless requested.
- Separate waits on a person, a decision, and a system. Name the owner or service instead of writing only `blocked`.

## Layout And State

Use the plan root already documented by the repository. Set `PLAN_ROOT` to that path; when no repository convention exists, use `research/plans/`:

```text
<plan-root>/
  README.md
  drafts/
  next/
  open/
  done/
  discarded/
```

The folder is the lifecycle source of truth and must match frontmatter `status`:

- `drafts`: captured or under investigation; open design questions are allowed.
- `next`: implementation-ready with decisions, dependencies, and checks resolved.
- `open`: dispatched or implemented; may be waiting on review, CI, release, or a ticket owner.
- `done`: completion rules below are satisfied.
- `discarded`: intentionally stopped, with a reason and replacement when one exists.

Existing Markdown files directly under `<plan-root>/` are legacy plans. Index them, but do not move or rewrite them without an explicit classification.

## People And Systems

- `Owner` is the default plan owner and final reviewer. The Prompter supplies the request and answers decisions that evidence cannot resolve. An implementation agent may make changes, but never self-merge.
- Record the actual issue assignee, code-reviewers, and service owner for each dependency. Do not turn one work item's assignee into a permanent team-wide default.
- Use the issue tracker, documentation system, source host, CI, release tooling, and deployment systems available to the repository. Name only the systems relevant to the plan.
- Plans may depend on containers, databases, identity providers, cloud services, local certificates, or manually supplied configuration. Name only the systems and prerequisites relevant to the plan, and never store their secrets.

## Naming

Every new plan filename must follow this pattern:

```text
iiot-<NUMBER>-<NAME>.md
```

- `<NUMBER>` is the issue number supplied by the Owner or source request. Never invent a number.
- When no number is supplied, use `XXXX` exactly: `iiot-XXXX-<NAME>.md`.
- `<NAME>` is a lowercase, hyphen-separated slug inferred from the request when necessary. Use no more than four words.
- Preserve the source title, identifier, and terminology in the plan contents and frontmatter even when the filename uses `XXXX`.
- Existing legacy filenames may be indexed, but must not be renamed automatically.

Examples: `iiot-2851-app-instances.md` and `iiot-XXXX-route-validation.md`.

## Plan File

Every plan starts with parseable YAML:

```yaml
---
id: null
title: <short title>
status: draft
owner: Owner
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []
repositories: []
branches: []
pull_requests: []
depends_on: []
blocked_by: []
---
```

Use `null` for an unknown `id`, and arrays even for one value. Never store credentials, tokens, or copied chat secrets.

A draft needs `Status`, `Summary`, `Sources`, `Context Snapshot`, and `Open Questions`. A plan in `next`, `open`, or `done` uses the fuller format below:

1. `# <ticket>: <title>`
2. `## Status` with landed, remaining, blocked, and evidence.
3. `## Summary` with problem, desired result, scope, non-goals, and compatibility.
4. `## Sources` with tickets, PRs, code, tests, docs, and relevant conversation evidence.
5. `## Diagram` with one useful Mermaid diagram.
6. `## Steps` with ordered phases, exact files or symbols, negative paths, and acceptance criteria.
7. `## Verification` with exact commands, prerequisites, and expected results.
8. `## Dependencies` split into people, decisions, systems, and other plans.
9. `## Estimations` in developer-hours, excluding external wait time.
10. `## Dispatch Log` with agent, branch, commits, PRs, checks, and blockers.
11. `## Outcome` with what landed, deviations, release evidence, and follow-up work.

## Evidence Sources And Commands

Use only sources available in the current session. State what could not be reached.

```bash
PLAN_ROOT="${PLAN_ROOT:-research/plans}"
find "$PLAN_ROOT" -maxdepth 2 -type f -name '*.md' -print | sort
git -C <repo> status --short --branch
git -C <repo> log --all -n 20 --date=short --format='%ad %h %s'
git -C <repo> diff --check
```

Use the configured connectors for the issue tracker, documentation system, source host, CI, release, and deployment systems when they are available. Record the exact command or tool call and its result. If a connector is unavailable, record that gap instead of inferring remote state. Use a bounded local session-history query when prior agent context is relevant and the tool is available.

Choose checks by affected repository and copy their exact forms from repository documentation:

```bash
<repository-test-command>
<repository-lint-command>
<repository-build-command>
<repository-integration-command>
<repository-smoke-command>
```

Replace every placeholder with a runnable command in the plan. State prerequisites such as container services, non-secret environment configuration, certificates, credentials, or external access. Use the lockfile and package manager already present in each repository.

## Completion Rule

Move a plan to `done` only when all planned acceptance criteria pass, required tests and real CI succeed, required reviews are complete, documentation and configuration match the shipped behavior, and any promised release or deployment is observed. Keep a plan in `open` when its issue, release, deployment, reviewer action, or external dependency is still pending. The Owner decides whether an explicit exception is acceptable.