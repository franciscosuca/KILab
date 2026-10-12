---
name: plan-write
description: "Investigate a draft or prepare the next bounded work package in an existing plan. Use for cross-repository features, bugs, migrations, documentation, and deployment changes before dispatch."
argument-hint: "<plan name, issue key, or topic> [wp-N]"
user-invocable: true
---

# Write An Implementation Plan

Read the sibling `plan-spec/SKILL.md` first. Before inspecting drafts, request context, or source code for this lifecycle task, pass its `PLAN_ROOT` fail-closed gate. If no valid absolute root is available, ask the user for it and stop; never guess a folder or continue under another root. Also read any repository-local planning guidance named by the project. This skill investigates and writes the plan; it does not implement it.

## Procedure

1. Resolve `PLAN_ROOT` and select one canonical bundle in `drafts`. With an explicit `wp-N`, also allow preparation in `next` or continuation in `open`; do not reopen `done` or `discarded` implicitly. Resolve the selector using `plan-spec`, not a separate `<ticket>-wp1` plan. If the plan or WP is ambiguous, show the candidates and ask. Without a selector, preserve any recorded WP boundary rather than resetting it to whole-plan execution. Do not treat supporting files as separate plans.
2. Before investigation, append the current `plan-write` input, supplied examples, constraints, and references to `<plan-bundle>/context/request.md`; preserve earlier entries. Then read the context and existing sources, identify the smallest implementation path that directly controls the behavior, and identify the nearest test that could disprove the current explanation.
3. Inspect current code, tests, schema, configuration, and relevant history. Check every affected repository or system boundary, such as service, client, extension, persistence, authentication, deployment, and documentation, as applicable.
4. Read the current external issue and cited documentation page when connectors are available. Compare remote and local content before planning documentation changes.
5. Classify discovered work as `landed`, `partially landed`, `planned`, or `blocked`. Keep landed work visible so an agent does not rebuild it.
6. Resolve implementation choices from repository evidence. Ask the Prompter only for product or architecture decisions that evidence cannot answer.
7. Write or update only the canonical Markdown file using the structure from `plan-spec`: YAML frontmatter, issue tag, Status, Summary, Diagram, Steps, Verification, Estimations, and Related documents with Context and Work packages subsections. Include one useful Mermaid diagram when the planned change introduces or changes project architecture, a component relationship, a data model, or a request or workflow flow. Choose the diagram type that fits the change, such as `sequenceDiagram`, `flowchart`, or `erDiagram`; show only what is new or changed in the project architecture rather than creating separate current-state and target-state diagrams. Keep the work-package folder empty during the initial pass and preserve existing supporting documents on later passes. Do not create work packages until the user explicitly asks for them. Include exact files and symbols, negative cases, exact verification commands, dependencies, estimates, and done criteria. For a selected WP, read any existing supporting definition, record its proposed boundary and actual approval coverage in Execution scope, name the exact branch/base and checks, and retain all other phases as planned/context. Preparing a scope is not approval; leave it unapproved until the user approves it. Resolve contradictions before dispatch; do not silently rewrite the supporting WP or earlier implementation evidence.
8. Check recurring failure points explicitly: package manager and working directory, lockfile, CI/release runner, required secrets or identity, container entrypoint, runtime mocks, and local/remote documentation drift.
9. For a first dispatch, keep the bundle in `drafts` until the canonical overall boundary and the selected execution scope are approved and implementation-ready. Then mark the selected WP `ready` when scoped, move the complete directory to `next`, update canonical status, and leave supporting folders intact. Record genuinely later-WP gates in their WP rows; shared blockers remain canonical `blocked_by`. For a continuation, leave an `open` bundle in `open` (and an existing `next` bundle in `next`), mark only the selected WP `ready` when its approval/dependency gates pass, or record its blocker and owner. Do not move an open plan backward, approve unrelated WPs, or change `in-progress`/`in-review`/`verified` evidence without an explicit rework request.
10. Set `updated`, append a History line including `wp-N` when scoped and the resulting folder/readiness, then update the single index entry. Preserve earlier History, Dispatch Log, and Outcome evidence. Do not change product code or commit.

Before moving a draft, verify that the bundle and canonical file both follow `<PREFIX>-<NUMBER>-<NAME>`; the canonical file is `<PREFIX>-<NUMBER>-<NAME>.md`. `<PREFIX>` is the configured plan prefix, defaulting to `plan`; accept existing bundles with other prefixes as they are. Use `<PREFIX>-XXXX-<inferred-name>` when no issue number was supplied, with at most four lowercase hyphen-separated name words. Do not silently rename an existing legacy draft or bundle; report the mismatch and ask the Prompter before changing it.

## Next Command

Finish with one `Next:` line:

- Whole plan moved to `next/`: `Next: /plan-dispatch <slug>`.
- Selected WP is approved and ready in `next/` or `open/`: `Next: /plan-dispatch <slug> wp-N`.
- Scope still needs approval, evidence, or a dependency: name that gate and its owner, then `Next: /plan-write <slug> wp-N` when scoped, or `/plan-write <slug>` otherwise. A recorded next WP is not permission to start it automatically.

## Commands

Run these only after the `PLAN_ROOT` gate passes. Use the narrowest relevant forms:

```bash
if [ -z "${PLAN_ROOT:-}" ] || [ "${PLAN_ROOT#/}" = "$PLAN_ROOT" ] || [ ! -d "$PLAN_ROOT" ]; then
  printf 'PLAN_ROOT must be a configured absolute existing directory; ask the user and stop.\n' >&2
  exit 2
fi
# Default to drafts; inspect next/open only for an explicitly selected WP.
find "$PLAN_ROOT/<current-lifecycle>" -mindepth 2 -maxdepth 2 -type f -name '*.md' -print | sort
grep -RniE '<symbol|route|setting|ticket>' <repo-path>
git -C <repo> status --short --branch
git -C <repo> log --all -n 30 --date=short --format='%ad %h %s' -- <path>
git -C <repo> blame -L <start>,<end> -- <path>
<issue-tracker-lookup-command>
<documentation-lookup-command>
# First approval only; never move an open continuation backward.
mv "$PLAN_ROOT/drafts/<plan-slug>" "$PLAN_ROOT/next/<plan-slug>"
```

Use the editor's search first; `grep -RniE` is the shell fallback when a faster search tool is unavailable. Copy the applicable test, build, container, and smoke commands from repository documentation into `## Verification`; do not write placeholders such as "run tests".

## Ready Gate

For whole-plan execution, the canonical plan is ready for approval only when scope and non-goals are explicit, current behavior is evidenced, dependencies and owners are named, each phase has acceptance criteria, commands are runnable in the named repository, Related documents subsections exist even when empty, and no unresolved decision can change the implementation shape. Empty supporting folders are expected on the initial pass.

For WP execution, require an approved overall scope/architecture plus the selected WP's exact files/shared changes, non-goals, branch/base, dependencies, acceptance criteria, and checks. Record approval coverage in Execution scope. Later WPs may remain planned or blocked only when their open questions cannot change this slice; preserve their scope and the whole-plan completion criteria. Preparing one WP does not authorize the remaining WPs or make the parent plan complete.