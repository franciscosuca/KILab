# Plan Skills Workflow

The plan skills manage implementation work under `PLAN_ROOT`. The lifecycle folders are:

## Required PLAN_ROOT Gate (Every Stage)

Before any planning-lifecycle stage—including init, add, write, dispatch, status, sync, retro, or creating supporting workflows/work packages—resolve a non-empty absolute `PLAN_ROOT` from the current request/conversation, explicit repository/workspace configuration, or an environment value visible to the agent. Do not rely on a value remembered from another conversation or another machine.

If no valid path is available, stop before searching, reading, or changing plan data and ask: `What absolute path should I use for PLAN_ROOT?` Wait for the user's answer. Never guess a folder, use the repository root as a fallback, or create a candidate location. If a configured path is invalid or inaccessible, ask for a correction rather than falling back. Only `/plan-init` may create the specified root, and only after the gate passes; every other stage requires the specified root to exist. If it or expected lifecycle folders are missing, stop and direct the user to `/plan-init` rather than initializing implicitly.

The canonical policy is in `plan-spec/SKILL.md` and applies even when a stage is invoked through a prompt example below.

- `drafts/`: captured requests and canonical plans that still need investigation or approval.
- `next/`: approved plan bundles with a whole-plan or explicitly bounded first-WP scope ready for dispatch.
- `open/`: dispatched or implemented plans with remaining WPs or review, CI, release, deployment, or other dependencies.
- `done/`: plans whose acceptance criteria and completion evidence are verified.
- `discarded/`: plans intentionally stopped with a reason and, when available, a replacement link.

`Blocked` is an index category, not a folder. A blocked plan stays in the lifecycle folder that matches its current status and records `blocked_by` in the canonical file.

## Plan Bundle Structure

Each plan is a bundle. The canonical file is the only lifecycle owner; supporting documents are not separate plans.

```text
<PLAN_ROOT>/<lifecycle>/<plan-slug>/
├── <plan-slug>.md
├── context/
│   └── request.md
├── workflows/
└── work-packages/
```

`workflows/` and `work-packages/` remain empty during the initial draft pass. The canonical file is created first and includes empty Related documents subsections for Context, Work packages, and Workflows.

The original request is preserved in `context/request.md`. Workflow documents are created only after the user approves the canonical plan. Work packages are created only after the user explicitly requests them.

## Filename Rule

Every new plan uses the same slug for its bundle directory and canonical file:

```text
<plan-slug>/<plan-slug>.md
```

For plans with an issue number:

```text
<PREFIX>-<NUMBER>-<NAME>/<PREFIX>-<NUMBER>-<NAME>.md
```

For plans without an issue number:

```text
<PREFIX>-XXXX-<inferred-name>/<PREFIX>-XXXX-<inferred-name>.md
```

`<PREFIX>` is the plan prefix configured for the plan root (`Plan prefix:` in `<PLAN_ROOT>/README.md`) or named in the request; when nothing defines one, use `plan`. For example, `Plan prefix: iiot` yields `iiot-1212-balbla/iiot-1212-balbla.md`. `<NAME>` is a lowercase, hyphen-separated slug inferred from the request, with no more than four words. Work packages use `wp-<N>-<short-description>.md`. Existing bundles keep their prefix; legacy files are indexed or archived but are not renamed automatically.

## Lifecycle States And Commands

```mermaid
flowchart LR
    init["/plan-init"] --> draftsBox

    subgraph draftsBox["drafts/"]
        add["/plan-add"]
        writeDraft["/plan-write slug"]
        add --> writeDraft
    end

    subgraph nextBox["next/"]
        dispatchWhole["/plan-dispatch slug"]
    end

    subgraph openBox["open/"]
        direction TB
        status["/plan-status"]
        sync["/plan-sync slug"]
        writeWP["/plan-write slug wp-N"]
        dispatchWP["/plan-dispatch slug wp-N"]
        status ~~~ sync ~~~ writeWP ~~~ dispatchWP
        writeWP <--> dispatchWP
    end

    subgraph doneBox["done/"]
        retroDone["/plan-retro"]
    end

    subgraph discardedBox["discarded/"]
        retroDiscarded["/plan-retro"]
    end

    writeDraft -->|"approved"| nextBox
    dispatchWhole -->|"dispatch"| sync
    dispatchWhole --> writeDraft
    sync -->|"whole plan verified"| doneBox
    sync -->|"abandoned, confirmed"| discardedBox
```

Each folder under `PLAN_ROOT` is one lifecycle state. Only the command in the last column moves a plan out of its current folder; WP preparation, dispatch, and synchronization may update an open plan in place without moving it.

| Folder | Meaning | Reached by | Run next | Leaves through |
|---|---|---|---|---|
| `drafts/` | Request captured; investigation or approval pending | `/plan-add` | `/plan-write <slug>` | `/plan-write` after approval → `next/` |
| `next/` | Whole plan or approved first WP ready for dispatch | `/plan-write` (approval) | `/plan-dispatch <slug>` for whole-plan mode; `/plan-dispatch <slug> wp-N` for a bounded WP | `/plan-dispatch` → `open/` |
| `open/` | Work dispatched; remaining WPs or acceptance evidence pending | `/plan-dispatch` | `/plan-status` to check; `/plan-sync <slug>` to verify evidence; `/plan-write <slug> wp-N` then `/plan-dispatch <slug> wp-N` for a subsequent WP | `/plan-sync` → `done/` only when the whole plan is verified, or → `discarded/` when abandonment is confirmed |
| `done/` | Acceptance criteria and completion evidence verified | `/plan-sync` | `/plan-retro` | Terminal |
| `discarded/` | Intentionally stopped, with a reason and replacement when one exists | `/plan-sync` after confirmation | `/plan-retro` | Terminal |

Commands that do not change state:

- `/plan-init` creates the root and lifecycle folders once. Run it before any other command.
- `/plan-status` is read-only. Run it at any point to see which folder each plan is in and what it waits on.
- `/plan-retro` reads `done/` and `discarded/` and proposes skill edits. It moves nothing.
- `/plan-write <slug> wp-N` and `/plan-dispatch <slug> wp-N` can prepare/execute another WP in `open/`; neither moves an open bundle backward.

## Work-Package-By-Work-Package Execution

Keep one canonical plan and one lifecycle/index entry for the feature. Use a positional `wp-N` selector to prepare or dispatch exactly one WP already defined in the canonical Steps or linked supporting document. Do not create a separate `<ticket>-wp1` plan or move a supporting WP file between lifecycle folders.

`plan-spec` defines the canonical `## Execution scope` table and WP progress states: `planned`, `ready`, `in-progress`, `in-review`, `verified`, and `blocked`. Record approval coverage, dependencies, the bounded implementation scope, branch/base, exact checks, and evidence there or in the canonical Verification/Dispatch Log. Later WPs stay visible but are not authorized by the current dispatch. Empty supporting folders are still valid for whole-plan execution; a WP selector does not implicitly create a file.

The first approved slice moves the entire bundle `drafts → next → open`. Subsequent slices stay in `open`: prepare/approve the next WP, dispatch it explicitly, verify its evidence, and repeat. Dependencies require verified predecessor evidence unless explicitly approved as parallel-safe with isolated ownership. Do not automatically start another WP after a handoff, or widen a WP-mode plan to whole-plan dispatch when its selector is omitted.

`/plan-sync` may verify a WP while keeping the parent open. A completed WP, or its merged PR alone, does not complete the feature; every required WP and the combined plan-level criteria must pass before `done`.

## Examples

Stage-by-stage prompt examples are in [EXAMPLES.md](EXAMPLES.md).

## Safety Rules

- The Owner is the default plan owner and final reviewer; the Prompter supplies decisions that evidence cannot resolve.
- At every lifecycle stage, require a valid absolute `PLAN_ROOT`; if it is missing, ask the user and stop without touching plan data. Never infer a fallback path.
- Never invent an issue number. Use `XXXX` when it is missing.
- Never store credentials, tokens, or secret-bearing conversation text in a plan.
- Do not rename or rewrite legacy plans during initialization.
- Do not treat context, workflow, or work-package files as separate lifecycle plans.
- Do not create workflows before canonical-plan approval.
- Do not create work packages without an explicit user request.
- Require explicit WP selection and recorded scope approval for bounded dispatch; never widen it, auto-run prerequisites, or start the next WP automatically.
- Keep shared blockers at plan level; do not hide them as deferred-WP gates.
- Keep the complete bundle open until every required WP and the combined completion criteria are verified.
- Do not merge reviews, transition external work items, trigger releases, or deploy merely to make a plan appear complete.
