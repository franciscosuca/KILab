---
name: plan-spec
description: "Shared contract for repository plan folders, plan Markdown, lifecycle states, evidence sources, dependencies, and completion checks. Every plan-* skill must read this first."
user-invocable: false
disable-model-invocation: true
---

# Plan Specification

Read this file before using any other `plan-*` skill in this feature-planning collection. The plan file is the durable handoff between the Prompter, Owner, implementation agent, source control, CI, and any external systems named by the plan.

## Working Rules Learned From History

- Start with the user or system problem, then the desired workflow or result. Preserve screenshots, examples, current-versus-desired behavior, and explicit alternatives.
- Inspect the real implementation, schema, tests, and remote source before changing a plan or documentation. A local note or external page is context, not proof that behavior shipped.
- Keep wording short and technical. Preserve source terminology and external identifiers. Do not expand the scope to adjacent cleanup without naming it.
- When the Prompter says proceed, apply the approved change and validate it. Do not stop after repeating a proposal.
- Record every command that was run. A pipeline edit is not verified until its underlying build or test runs locally where possible and the real CI policy succeeds.
- Recheck package manager, lockfile, working directory, release runner, credentials, container startup command, and runtime environment. These commonly cause follow-up fixes.
- If documentation or a diagram mirrors an external source, compare both directions before calling it current. Do not replace editable diagrams with screenshots unless requested.
- Separate waits on a person, a decision, and a system. Name the owner or service instead of writing only `blocked`.
- For factual audit entries, copy IDs, refs, states, timestamps, and check results from the authoritative output for that event. Distinguish approval, observation, and mutation times; do not infer current repository state from an earlier snapshot or reconstruct one opaque ID from another. Mark unverifiable facts as unverified and append corrections when needed.

## PLAN_ROOT Resolution And Fail-Closed Gate

Before any planning-lifecycle operation, resolve `PLAN_ROOT` from an absolute path supplied in the current request or conversation, an explicit repository/workspace configuration, or a non-empty `PLAN_ROOT` value visible to the current agent. A path remembered only from another conversation or unavailable machine environment does not count. Do not embed a user-specific absolute path in a skill or plan.

The value must be non-empty and absolute. Never infer it from the current directory, choose a repository-local default, search for a likely vault, or fall back to another folder. If no valid value is available, stop before searching, reading, or changing plan data and ask the user: `What absolute path should I use for PLAN_ROOT?` Wait for the answer; do not proceed with any lifecycle stage until it is supplied. If the supplied/configured path is inaccessible or invalid, stop and ask for a correction rather than trying another location.

`/plan-init` may create the specified root and lifecycle folders only after this gate passes. Every other lifecycle skill requires the specified root to exist; if it does not, stop and direct the user to `/plan-init` rather than creating anything implicitly. If expected lifecycle folders are missing, report that and do not initialize them implicitly. Recheck this gate independently at every lifecycle stage and in every new conversation.

## Layout And State

Once the gate passes, the plan root contains lifecycle folders:

```text
<plan-root>/
  README.md
  drafts/
  next/
  open/
  done/
  discarded/
```

Each new plan is a bundle whose directory and canonical file share the same slug:

```text
<plan-root>/<lifecycle>/<plan-slug>/
  <plan-slug>.md
  context/
    request.md
  work-packages/
```

`context/` stores the original request and related context; `work-packages/` contains optional supporting definitions. They are supporting-document areas, not independent plans. The canonical Markdown file is the only lifecycle and status owner. Move the complete bundle between lifecycle folders; never move only the canonical file.

New plan bundles do not create a separate `workflows/` directory or `Workflows` section. Existing bundles may contain those legacy artifacts; preserve them and their links during ordinary commands. Do not create, rewrite, or delete them unless the user explicitly asks to migrate or clean them up.

The lifecycle folder is the source of truth and must match canonical frontmatter `status`:

- `drafts`: request captured and canonical plan under investigation or awaiting approval.
- `next`: canonical plan approved and implementation-ready for the whole plan or its explicitly approved first work package; supporting documents may still be empty.
- `open`: dispatched or implemented; may contain remaining planned work packages or be waiting on review, CI, release, or a ticket owner.
- `done`: completion rules below are satisfied.
- `discarded`: intentionally stopped, with a reason and replacement when one exists.

Standalone Markdown files directly under a lifecycle folder are legacy plans. Index them, but do not move or rewrite them without an explicit classification.

## People And Systems

- `Owner` is the default plan owner and final reviewer. The Prompter supplies the request and answers decisions that evidence cannot resolve. An implementation agent may make changes, but never self-merge.
- Record the actual issue assignee, code-reviewers, and service owner for each dependency. Do not turn one work item's assignee into a permanent team-wide default.
- Use the issue tracker, documentation system, source host, CI, release tooling, and deployment systems available to the repository. Name only the systems relevant to the plan.
- Plans may depend on containers, databases, identity providers, cloud services, local certificates, or manually supplied configuration. Name only the systems and prerequisites relevant to the plan, and never store their secrets.

## Naming

The canonical plan bundle and file use the same name:

```text
<PREFIX>-<NUMBER>-<NAME>/
└── <PREFIX>-<NUMBER>-<NAME>.md
```

- `<PREFIX>` is the plan prefix. Resolve it from the current request, then from the `Plan prefix: <word>` line in `$PLAN_ROOT/README.md`; when neither defines one, use `plan` exactly. A prefix is a single lowercase hyphenated word, for example `iiot` gives `iiot-1212-<NAME>/iiot-1212-<NAME>.md`.
- `<NUMBER>` is the issue number supplied by the Owner or source request. Never invent a number.
- When no number is supplied, use `XXXX` exactly: `<PREFIX>-XXXX-<NAME>/<PREFIX>-XXXX-<NAME>.md`.
- `<NAME>` is a lowercase, hyphen-separated slug inferred from the request when necessary. Use no more than four words.
- Preserve the source title, identifier, and terminology in the canonical contents and frontmatter even when the filename uses `XXXX`.
- Work packages use `wp-<N>-<short-description>.md`, for example `wp-1-schema-registry.md`.
- Supporting documents share the canonical issue tag, for example `#plan-2789`.
- Existing bundles keep the prefix they were created with; changing the configured prefix applies to new plans only. Existing legacy filenames and folders may be indexed, but must not be renamed automatically.

## Plan Bundle And Canonical File

Only the canonical file starts with parseable YAML:

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

Use `null` for an unknown `id`, and arrays even for one value. Never store or render credentials, tokens, or copied chat secrets. Treat command output as potentially secret-bearing: do not print raw `git remote -v`, credential-bearing URLs/configuration, or secret-bearing environment values. Prefer remote names and read-only ref queries; redact embedded userinfo and credential query parameters before displaying a URL when necessary.

The canonical draft follows this structure:

1. `#<issue-id>` tag.
2. `# <ticket>: <title>`.
3. `## Status`.
4. `## Summary` with problem, desired result, scope, non-goals, and compatibility.
5. `## Diagram` with one useful Mermaid diagram.
6. `## Steps` with ordered phases, exact files or symbols, negative paths, and acceptance criteria.
7. `## Verification` with exact commands, prerequisites, and expected results.
8. `## Estimations` in developer-hours, excluding external wait time.
9. `## Related documents` with `Context` and `Work packages` subsections.
10. `## History`: append-only log with one line per command that changes the plan, formatted `- YYYY-MM-DD <command>: <result>`. `/plan-add` creates it; later commands append and never rewrite earlier lines.

The Related documents subsections must exist in the initial canonical file but may be empty. Add links only when the corresponding supporting files are created.

The first planning input is preserved in `context/request.md` before the canonical summary is written. The initial `plan-write` pass must not create work-package documents. Work packages require a separate explicit user request.

Supporting documents do not require YAML frontmatter. They begin with the shared issue tag. A work package begins with its title and then `## Goal`; do not insert automatic Plan mapping, Route model, or Source references blocks between the title and Goal.

Execution-only sections such as `Dependencies`, `Dispatch Log`, and `Outcome` may be added to the canonical file when the plan enters the corresponding lifecycle stage. They are not required in the initial draft template.

### Evidence Placement And Compactness

- Keep `Status` and `Execution scope` as concise current snapshots.
- When present, use `Dispatch Log` for per-attempt commands/results, IDs, review/check state, deviations, and blockers.
- Use `Outcome` for final reconciliation, exceptions, residuals, and the completion decision; cite the relevant dispatch entry, PR, or commit instead of duplicating detailed receipts.
- Keep each `History` line a concise mutation summary that points to detailed evidence rather than copying command output or full test results.
- Updating several sections does not require repeating the same detailed evidence; preserve earlier append-only records.

## Work-Package Execution

Whole-plan execution remains the default for plans without an active work-package boundary. An explicitly approved switch uses `Mode: whole-plan` and retains earlier WP/evidence records; omitting a selector is not such approval. To execute incrementally, use `/plan-write <slug> wp-N` to prepare one existing work package and `/plan-dispatch <slug> wp-N` to implement it. These are skill arguments, not new standalone plans or harness CLI flags. Resolve `wp-N` to exactly one definition in the canonical Steps or an existing linked `work-packages/wp-N-<description>.md`; stop and ask if it is missing, ambiguous, or contradicts the canonical scope. Never infer a new ticket or create a supporting file without the separate explicit request required above.

The canonical plan remains the only lifecycle and progress owner. Add `## Execution scope` when work-package execution is requested, retain every remaining phase, and record the approved overall boundary, the next proposed slice, and one row per defined WP. For example:

```markdown
## Execution scope
Mode: work-package
Plan approval: <approver, date, and approved overall scope>
Next dispatch: wp-1

| WP | Scope / supporting document | Dependencies | State | Approval / evidence / blockers |
| --- | --- | --- | --- | --- |
| wp-1 | <bounded scope or existing relative link> | none | ready | <approver/date; checks in Verification> |
| wp-2 | <remaining scope or existing relative link> | wp-1: verified | planned | Not approved for dispatch |
```

The table is ordinary Markdown, not additional YAML or independent lifecycle state. Keep repository/branch mappings and exact per-WP checks in the canonical plan; use `Dispatch Log` for each attempt's WP, timestamp, agent, branch/base, commits, review, command results, deviations, and blockers. Keep approval and verification evidence distinguishable. `Next dispatch` is a suggestion, not authorization to launch it.

WP progress states:

- `planned`: retained scope that is not yet approved and implementation-ready.
- `ready`: the bounded scope is approved, dependencies are satisfied or explicitly parallel-safe, and files, branch/base, acceptance criteria, and checks are exact.
- `in-progress`: the selected WP has been dispatched; do not start a duplicate writer.
- `in-review`: implementation and local checks are recorded, but review, real CI, or other WP acceptance evidence remains.
- `verified`: `/plan-sync` has confirmed that WP's acceptance criteria, required checks/reviews, and any WP-specific release/deployment promises pass. Overall ticket closure or a final combined release can remain a plan-level gate.
- `blocked`: record the person, decision, system, or implementation blocker and the previous progress state so it can be resumed deliberately.

Approval may cover the whole plan or a named slice, but its coverage must be recorded. For a scoped first dispatch, the overall scope/architecture must be approved and no unresolved decision may change the selected WP's implementation. Later WPs may remain planned or blocked only when their unanswered questions cannot affect the approved slice. Canonical `depends_on` and `blocked_by` apply to every dispatch; genuinely WP-specific dependencies/blockers belong in the WP row. Never move a shared blocker into a later WP merely to bypass readiness.

A work-package-mode plan requires an explicit `wp-N` at dispatch. Omitting the selector must not widen the request to the whole plan; ask which WP to run. Switching back to whole-plan execution requires explicit user approval. Only the selected WP and its necessary, named shared changes are authorized; other WPs remain context. If an unplanned prerequisite is found, stop and ask rather than implementing it or automatically dispatching the next WP.

On the first dispatch, move the complete bundle from `next` to `open` once. Subsequent WP preparation/dispatch stays in `open`; never move the bundle back to `drafts` or `next`, move individual WPs, or copy them into separate plans. Dependencies require `verified` predecessor evidence by default. Starting before verification requires explicit parallel-safe approval, named branch/base assumptions, and non-overlapping worktree/file ownership. Preserve previously verified results and recheck them when later changes invalidate their evidence.

Commands that mutate a canonical plan update its `updated`, Execution scope when present, applicable Dispatch Log/Outcome, append-only History, and the single index entry. Include the WP selector in scoped History entries. `/plan-status` only reports these records. One verified WP never makes the parent plan `done`; the whole-plan completion rule still applies.

## Evidence Sources And Commands

Run these commands only after the `PLAN_ROOT` gate above passes. If the value is absent or invalid, ask the user and stop; do not use a shell error as a substitute for that prompt. Use only sources available in the current session. State what could not be reached.

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
find "$PLAN_ROOT" -maxdepth 3 -type f -name '*.md' -print | sort
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

Move a plan to `done` only when all planned acceptance criteria pass, required tests and real CI succeed, required reviews are complete, documentation and configuration match the shipped behavior, and any promised release or deployment is observed. For work-package execution, verify every required WP and the combined plan-level criteria; the latest WP's PR alone is not whole-plan evidence. Keep a plan in `open` while any required WP is planned, ready, in-progress, in-review, blocked, or unverified, or when its issue, release, deployment, reviewer action, or external dependency is still pending. The Owner decides whether an explicit exception is acceptable; record the exact exception without silently deleting deferred scope.