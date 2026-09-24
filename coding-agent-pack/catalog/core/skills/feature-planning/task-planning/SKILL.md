---
name: task-planning
description: "Use when creating or updating implementation-ready plans across one or more repositories, services, or deployment environments."
---

# Task Planning

Create implementation-ready plans from the current state of the repository or workspace. Plans belong under the configured `PLAN_ROOT` and are stored as plan bundles: one canonical Markdown file plus optional context, workflow, and work-package documents. Plans must be based on the code, tests, configuration, and relevant history rather than on an issue description alone.

This skill produces a plan. Do not implement the planned changes unless the user explicitly asks for implementation.

## Repository Scope

Treat each repository, package, service, client, extension, infrastructure boundary, and documentation system as separate when that helps identify ownership or verification. Read repository-local instructions before planning. Research notes and external references are useful context but are not proof that behavior has shipped.

Read the repository's local instructions before planning. Check for `copilot-instructions.md`, `AGENTS.md`, and project-specific contribution or testing documentation in the paths affected by the task.

## Planning Workflow

1. **Capture the request.** Preserve the incoming request, examples, constraints, and named references in the plan bundle's `context/request.md` before writing the canonical summary. Then record the requested behavior, affected users or services, explicit non-goals, and constraints.
2. **Inspect current behavior.** Read the owning implementation, its neighboring tests, relevant schemas or configuration, and the closest documentation. Follow the request or lifecycle through each boundary instead of planning from filenames alone.
3. **Check history.** Use the latest relevant commits and, when useful, blame or earlier task notes to distinguish work that is already landed from work that is only proposed. Do not treat an old plan as current status.
4. **Classify each work item.** Mark it as `landed`, `partially landed`, `planned`, or `blocked`. For `landed` items, cite the path and symbol that demonstrate the behavior and note whether tests cover it. Preserve landed work in the plan so the remaining scope is unambiguous.
5. **Trace cross-project effects.** Check API contracts, authentication and authorization, persistence and migrations, startup or hydration, deployment configuration, frontend consumers, extension manifests, and compatibility with existing routes or resources when relevant.
6. **Write the canonical plan.** Order phases by dependency. Each phase must identify the behavior, likely files and symbols, tests, and operational or documentation work needed to complete it. Do not create workflow or work-package files during this first pass.
7. **Validate the canonical document.** Confirm that paths and symbols exist or are clearly labeled as new, Mermaid syntax is coherent, estimates cover discovery through verification, Related documents subsections exist even when empty, and no phase contradicts the current status.

## Required Plan Format

The canonical file in every plan bundle must use this structure:

1. YAML frontmatter with issue, title, status, owner, dates, sources, repositories, branches, pull requests, dependencies, and blockers.
2. `#<issue-id>` shared tag.
3. `# <ticket>: <title>`.
4. `## Status` with current state, remaining work, evidence, and blockers.
5. `## Summary` with problem, desired result, affected projects, scope, non-goals, compatibility, risks, and decisions.
6. `## Diagram` with one concise Mermaid diagram when the plan changes an architecture, component relationship, data model, request, or workflow.
7. `## Steps` with dependency-ordered phases.
8. `## Verification` with focused checks, commands, prerequisites, and expected results.
9. `## Estimations` with one row per phase and a total.
10. `## Related documents` containing empty or populated `Context`, `Work packages`, and `Workflows` subsections.

The first `plan-write` pass writes only the canonical file after preserving the incoming request in `context/request.md`. It must not create workflow documents or work packages automatically. Workflows require explicit approval of the canonical plan, and work packages require a separate explicit user request.

For every phase, specify:

- **Goal:** the behavior or decision the phase delivers;
- **Implementation surface:** existing or new repository-relative files, symbols, schemas, routes, configuration, or deployment resources;
- **Behavior and compatibility:** validation, error handling, security, data migration, rollout, and backward-compatibility requirements as applicable;
- **Verification:** focused unit, integration, API, browser, contract, or end-to-end tests, plus the relevant command when it is known;
- **Documentation or operations:** updates to specs, environment variables, deployment, observability, or rollback procedures when needed.

Supporting documents are not separate plans. They begin with the canonical issue tag. Work packages use `wp-<N>-<short-description>.md` and begin with a title followed directly by `## Goal`; do not add automatic Plan mapping, Route model, or Source references blocks.

## Context-Specific Checks

Apply the checks relevant to the task instead of assuming every task needs every item:

- **Backend or API:** routes, schemas, auth and authorization, error responses, persistence, migrations, startup hydration, configuration, and API documentation.
- **Extension behavior:** manifest or contract compatibility, route visibility, lifecycle enable or disable behavior, upstream communication, and sample-extension coverage.
- **Frontend:** API contract changes, loading and error states, validation, permissions, component tests, browser tests, and responsive or accessibility impact when user-facing.
- **Platform or deployment:** environment variables, secrets, ports, identity providers, networking, health checks, startup order, observability, and rollback.
- **Shared changes:** every consumer of the changed contract, versioning or migration strategy, and the smallest safe rollout order.

Do not invent implementation details to fill a gap. Mark unknowns as assumptions or open decisions and explain the check that will resolve them.

## Quality Bar

- Use exact repository-relative paths and symbol names whenever they are known.
- Prefer the existing abstractions, patterns, test fixtures, and tooling in the repository.
- Keep the plan specific enough that another developer can implement it without repeating the investigation.
- Make status claims falsifiable with nearby code or tests.
- Keep diagrams and estimates proportional to the change; avoid decorative content.
- Do not include secrets, generated credentials, or copied proprietary content in the plan.