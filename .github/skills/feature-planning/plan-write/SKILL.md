---
name: plan-write
description: "Investigate a draft and turn it into an implementation-ready plan. Use for cross-repository features, bugs, migrations, documentation, and deployment changes before dispatch."
argument-hint: "<draft name, issue key, or topic>"
user-invocable: true
---

# Write An Implementation Plan

Read `.github/skills/plan-spec/SKILL.md` first. Also read any repository-local planning guidance named by the project. This skill investigates and writes the plan; it does not implement it.

## Procedure

1. Resolve `PLAN_ROOT` and select one file in `$PLAN_ROOT/drafts/`. If the request is ambiguous, show the closest matches instead of guessing.
2. Read its sources, then identify the smallest implementation path that directly controls the behavior and the nearest test that could disprove the current explanation.
3. Inspect current code, tests, schema, configuration, and relevant history. Check every affected repository or system boundary, such as service, client, extension, persistence, authentication, deployment, and documentation, as applicable.
4. Read the current external issue and cited documentation page when connectors are available. Compare remote and local content before planning documentation changes.
5. Classify discovered work as `landed`, `partially landed`, `planned`, or `blocked`. Keep landed work visible so an agent does not rebuild it.
6. Resolve implementation choices from repository evidence. Ask the Prompter only for product or architecture decisions that evidence cannot answer.
7. Write the complete plan format from `plan-spec`, including one useful Mermaid diagram when the planned change introduces or changes project architecture, a component relationship, a data model, or a request or workflow flow. Choose the diagram type that fits the change, such as `sequenceDiagram`, `flowchart`, or `erDiagram`; show only what is new or changed in the project architecture rather than creating separate current-state and target-state diagrams. Also include exact files and symbols, negative cases, exact verification commands, dependencies, estimates, and done criteria.
8. Check recurring failure points explicitly: package manager and working directory, lockfile, CI/release runner, required secrets or identity, container entrypoint, runtime mocks, and local/remote documentation drift.
9. Move the file to `$PLAN_ROOT/next/` only when an implementation agent can proceed without a design question. Otherwise keep it in `drafts/`, set `blocked_by`, and name the owner or system.
10. Update the index. Do not change product code or commit.

Before moving a draft, verify that its filename follows `iiot-<NUMBER>-<NAME>.md`. Use `iiot-XXXX-<inferred-name>.md` when no issue number was supplied, with at most four lowercase hyphen-separated name words. Do not silently rename an existing legacy draft; report the mismatch and ask the Prompter before changing it.

## Commands

Use the narrowest relevant forms:

```bash
PLAN_ROOT="${PLAN_ROOT:-research/plans}"
find "$PLAN_ROOT/drafts" -maxdepth 1 -type f -name '*.md' -print | sort
grep -RniE '<symbol|route|setting|ticket>' <repo-path>
git -C <repo> status --short --branch
git -C <repo> log --all -n 30 --date=short --format='%ad %h %s' -- <path>
git -C <repo> blame -L <start>,<end> -- <path>
<issue-tracker-lookup-command>
<documentation-lookup-command>
mv "$PLAN_ROOT/drafts/<plan>.md" "$PLAN_ROOT/next/<plan>.md"
```

Use the editor's search first; `grep -RniE` is the shell fallback when a faster search tool is unavailable. Copy the applicable test, build, container, and smoke commands from repository documentation into `## Verification`; do not write placeholders such as "run tests".

## Ready Gate

A plan is ready only when scope and non-goals are explicit, current behavior is evidenced, dependencies and owners are named, each phase has acceptance criteria, commands are runnable in the named repository, and no unresolved decision can change the implementation shape.