---
name: task-planning
description: "Use when creating or updating implementation-ready plans across one or more repositories, services, or deployment environments."
---

# Task Planning

Create implementation-ready plans from the current state of the repository or workspace. Plans belong in `research/plans/` and must be based on the code, tests, configuration, and relevant history rather than on an issue description alone.

This skill produces a plan. Do not implement the planned changes unless the user explicitly asks for implementation.

## Repository Scope

Treat each repository, package, service, client, extension, infrastructure boundary, and documentation system as separate when that helps identify ownership or verification. Read repository-local instructions before planning. Research notes and external references are useful context but are not proof that behavior has shipped.

Read the repository's local instructions before planning. Check for `copilot-instructions.md`, `AGENTS.md`, and project-specific contribution or testing documentation in the paths affected by the task.

## Planning Workflow

1. **Define the change.** Record the requested behavior, affected users or services, explicit non-goals, and any constraints. Identify the smallest concrete code path or symbol that controls the behavior.
2. **Inspect current behavior.** Read the owning implementation, its neighboring tests, relevant schemas or configuration, and the closest documentation. Follow the request or lifecycle through each boundary instead of planning from filenames alone.
3. **Check history.** Use the latest relevant commits and, when useful, blame or earlier task notes to distinguish work that is already landed from work that is only proposed. Do not treat an old plan as current status.
4. **Classify each work item.** Mark it as `landed`, `partially landed`, `planned`, or `blocked`. For `landed` items, cite the path and symbol that demonstrate the behavior and note whether tests cover it. Preserve landed work in the plan so the remaining scope is unambiguous.
5. **Trace cross-project effects.** Check API contracts, authentication and authorization, persistence and migrations, startup or hydration, deployment configuration, frontend consumers, extension manifests, and compatibility with existing routes or resources when relevant.
6. **Write the plan.** Order phases by dependency. Each phase must identify the behavior, likely files and symbols, tests, and operational or documentation work needed to complete it.
7. **Validate the document.** Confirm that paths and symbols exist or are clearly labeled as new, Mermaid syntax is coherent, estimates cover discovery through verification, and no phase contradicts the current status.

## Required Plan Format

Use these headings in every task plan. Add a short ticket or issue title as the first heading.

### Status

Start with one status label: `not started`, `partially landed`, `largely landed`, `complete`, or `blocked`.

Then summarize:

- what is already present in the current code;
- what remains to be implemented or verified;
- the evidence used, including repository-relative paths, symbols, tests, or relevant commits;
- blockers, stale documentation, or assumptions that affect the status.

Do not call work complete until the implementation, relevant tests, and required configuration or documentation have been checked.

### Summary

Describe the intended outcome and scope in a few focused paragraphs or bullets. Include:

- the user or system problem;
- affected top-level projects and integration boundaries;
- in-scope behavior and explicit non-goals;
- dependencies, compatibility requirements, risks, and open decisions.

### Diagram

Include one concise Mermaid diagram that explains the most important relationship introduced or changed by the plan. Choose the diagram type that fits the problem:

- `flowchart` for lifecycle, branching, or deployment flow;
- `sequenceDiagram` for request, authentication, proxy, or service interactions;
- `erDiagram` for database entities and relationships;
- `stateDiagram-v2` for lifecycle or status transitions.

Label real components and boundaries. Keep the diagram readable and avoid inventing components that the plan does not need. Use simple Mermaid-safe labels when paths or punctuation could make syntax ambiguous.

### Steps

Organize the work into numbered phases in dependency order. For every phase, specify:

- **Goal:** the behavior or decision the phase delivers;
- **Implementation surface:** existing or new repository-relative files, symbols, schemas, routes, configuration, or deployment resources;
- **Behavior and compatibility:** validation, error handling, security, data migration, rollout, and backward-compatibility requirements as applicable;
- **Verification:** focused unit, integration, API, browser, contract, or end-to-end tests, plus the relevant command when it is known;
- **Documentation or operations:** updates to specs, environment variables, deployment, observability, or rollback procedures when needed.

Separate already-landed work from remaining work. Include negative paths and regression cases, not only the successful path. If a decision is unresolved, make it an explicit decision point with the information needed to resolve it.

### Estimations

Estimate effort in developer-hours for one developer. Use a table with one row per phase and a total. Include discovery, implementation, tests, migrations or configuration, documentation, and integration verification where they apply. Ranges are acceptable when uncertainty is real; state the assumptions and exclude external approvals or unavailable dependencies from the total.

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