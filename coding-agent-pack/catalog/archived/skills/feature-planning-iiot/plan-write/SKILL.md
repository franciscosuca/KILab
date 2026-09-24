---
name: plan-write
description: "Investigate a draft and turn it into an implementation-ready plan. Use for cross-repository features, bugs, migrations, documentation, and deployment changes before dispatch."
argument-hint: "<draft name, issue key, or topic>"
user-invocable: true
---

# Write An Implementation Plan

Read `.github/skills/plan-spec/SKILL.md` first. Also read any repository-local planning guidance named by the project. This skill investigates and writes the plan; it does not implement it.

## Procedure

1. Resolve `PLAN_ROOT` and select one canonical file in a plan bundle under `$PLAN_ROOT/drafts/<plan-slug>/<plan-slug>.md`. If the request is ambiguous, show the closest bundles instead of guessing. Do not treat context, workflow, or work-package files as separate plans.
2. Before investigation, append the current `plan-write` input, supplied examples, constraints, and references to `<plan-bundle>/context/request.md`; preserve earlier entries. Then read the context and existing sources, identify the smallest implementation path that directly controls the behavior, and identify the nearest test that could disprove the current explanation.
3. Inspect current code, tests, schema, configuration, and relevant history. Check every affected repository or system boundary, such as service, client, extension, persistence, authentication, deployment, and documentation, as applicable.
4. Read the current external issue and cited documentation page when connectors are available. Compare remote and local content before planning documentation changes.
5. Classify discovered work as `landed`, `partially landed`, `planned`, or `blocked`. Keep landed work visible so an agent does not rebuild it.
6. Resolve implementation choices from repository evidence. Ask the Prompter only for product or architecture decisions that evidence cannot answer.
7. Write or update only the canonical Markdown file using the structure from `plan-spec`: YAML frontmatter, issue tag, Status, Summary, Diagram, Steps, Verification, Estimations, and Related documents with Context, Work packages, and Workflows subsections. Include one useful Mermaid diagram when the planned change introduces or changes project architecture, a component relationship, a data model, or a request or workflow flow. Choose the diagram type that fits the change, such as `sequenceDiagram`, `flowchart`, or `erDiagram`; show only what is new or changed in the project architecture rather than creating separate current-state and target-state diagrams. Keep workflow and work-package folders empty during this pass. Do not create workflow files until the user approves the canonical plan, and do not create work packages until the user explicitly asks for them. Include exact files and symbols, negative cases, exact verification commands, dependencies, estimates, and done criteria in the canonical file.
8. Check recurring failure points explicitly: package manager and working directory, lockfile, CI/release runner, required secrets or identity, container entrypoint, runtime mocks, and local/remote documentation drift.
9. Keep the bundle in `$PLAN_ROOT/drafts/` until the user approves the canonical plan and an implementation agent can proceed without a design question. When ready, move the complete directory to `$PLAN_ROOT/next/<plan-slug>/`, update the canonical status, and leave supporting folders intact. Otherwise keep the bundle in `drafts/`, set `blocked_by`, and name the owner or system.
10. Update the index. Do not change product code or commit.

Before moving a draft, verify that the bundle and canonical file both follow `iiot-<NUMBER>-<NAME>`; the canonical file is `iiot-<NUMBER>-<NAME>.md`. Use `iiot-XXXX-<inferred-name>` when no issue number was supplied, with at most four lowercase hyphen-separated name words. Do not silently rename an existing legacy draft or bundle; report the mismatch and ask the Prompter before changing it.

## Commands

Use the narrowest relevant forms:

```bash
PLAN_ROOT="${PLAN_ROOT:?Set PLAN_ROOT to the configured planning root}"
find "$PLAN_ROOT/drafts" -mindepth 2 -maxdepth 2 -type f -name '*.md' -print | sort
grep -RniE '<symbol|route|setting|ticket>' <repo-path>
git -C <repo> status --short --branch
git -C <repo> log --all -n 30 --date=short --format='%ad %h %s' -- <path>
git -C <repo> blame -L <start>,<end> -- <path>
<issue-tracker-lookup-command>
<documentation-lookup-command>
mv "$PLAN_ROOT/drafts/<plan-slug>" "$PLAN_ROOT/next/<plan-slug>"
```

Use the editor's search first; `grep -RniE` is the shell fallback when a faster search tool is unavailable. Copy the applicable test, build, container, and smoke commands from repository documentation into `## Verification`; do not write placeholders such as "run tests".

## Ready Gate

A canonical plan is ready for user approval only when scope and non-goals are explicit, current behavior is evidenced, dependencies and owners are named, each phase has acceptance criteria, commands are runnable in the named repository, Related documents subsections exist even when empty, and no unresolved decision can change the implementation shape. Empty workflow and work-package folders are expected at this stage.