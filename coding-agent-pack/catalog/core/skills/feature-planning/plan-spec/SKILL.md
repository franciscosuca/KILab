---
name: plan-spec
description: "Internal feature-planning v2 contract: explicit root, one two-view plan, approval revisions, evidence, lifecycle, and mandatory next-command recommendations. Read before every planning operation."
user-invocable: false
disable-model-invocation: true
---

# Feature-planning v2 Contract

The canonical `plan.md` is the durable implementation handoff. Its metadata and `agent-version` own the contract; `tldr-version` is a derived human view. Read this contract before every planning command. No runtime extension or delegation framework is required.

## Root Gate — Before Any Plan Data Access

Resolve `PLAN_ROOT` from the current request/conversation, explicit repository/workspace configuration, or a non-empty environment value visible in this session. Require an absolute path. Never infer it from the working directory, search for a vault, rely on another session's memory, or fall back to another root. If missing, ask `What absolute path should I use for PLAN_ROOT?` and stop before scanning, reading, or changing plan data. If inaccessible or invalid, ask for correction and stop. Recheck in every conversation and at every stage.

Only `plan-create` may initialize that explicitly selected root. Idempotently add missing lifecycle folders and missing index sections; preserve all existing content and unrelated entries. Other commands require the root, index, and lifecycle folders to exist; otherwise recommend `plan-create` to initialize them first. Do not initialize Git or commit bookkeeping implicitly.

## Bundle, Naming, And Lifecycle

```text
<PLAN_ROOT>/
├── README.md
├── drafts/
├── next/
├── open/
├── done/
└── discarded/

<lifecycle>/<plan-slug>/
├── plan.md
└── artifacts/
    └── request.md
```

Only `plan.md` owns lifecycle/status. Artifacts are evidence, not plans. New bundles have only `plan.md` and `artifacts/` at their top level. Do not create separate audience files, work packages, work-package selectors/tables, workflow documents, or equivalent shadow plans inside artifacts. Use numbered inline implementation steps and checkpoints instead.

New slugs: `<prefix>-<number>-<name>`. Resolve prefix from the current request, then `Plan prefix: <word>` in the index, otherwise `plan`. Never invent an issue number: use `XXXX` when absent. Infer at most four lowercase hyphen-separated name words. Preserve exact external IDs/titles in metadata. Detect collisions; ask instead of overwriting or inventing a disambiguating issue. Existing slugs/prefixes remain unchanged.

Select exactly one canonical bundle by explicit slug or unambiguous issue/request match. Search all lifecycle folders for duplicates before creating. Never auto-select another queued plan, treat supporting files as plans, or interpret an extra execution selector as permission to widen scope.

| Folder | `status` | Meaning / transition owner |
| --- | --- | --- |
| `drafts/` | `draft` | Investigation, material decisions, readiness, or approval missing; `plan-create` may approve/prepare it. |
| `next/` | `next` | Current scope revision explicitly approved; implementation-ready. `plan-execute` starts work. |
| `open/` | `open` | Execution started; implementation or acceptance outstanding. Resume/replan in place; never silently move backward. |
| `done/` | `done` | Whole-plan completion verified or exact Owner exceptions accepted through `plan-sync`. |
| `discarded/` | `discarded` | Explicit abandonment confirmed through `plan-sync`, with reason/replacement. |

The folder owns lifecycle; report metadata mismatches before doing work, never execute through one. Blocked is not a folder. Record current blocking person/decision/system/implementation and owner in `blocked_by`; distinguish execution blockers from later completion gates. Terminal plans are not reopened or redispatched implicitly.

Legacy standalone files or bundles without `schema_version: 2` are read-only/indexable. Do not mutate, execute, or synchronize them as v2. Ask for explicit per-bundle migration authorization; the collection's `MIGRATION.md` describes conversion. No second legacy execution model lives here.

## Canonical File And Approval

Start from the [template](templates/plan.md). Frontmatter uses one key per line with **JSON-compatible YAML values**: quoted strings, ISO date strings, integers, `null`, and inline arrays. This deliberate subset needs no YAML dependency and preserves exact values. Use `id: null` if unknown; arrays remain arrays even for one value.

Required metadata: `schema_version: 2`, `id`, `title`, `status`, `owner`, `created`, `updated`, `sources`, `repositories`, `branches`, `pull_requests`, `depends_on`, `blocked_by`, `scope_revision`, `approved_revision`, `approved_by`, `approved_at`.

- `scope_revision` starts at 1. Increment for changed implementation boundaries, decisions, required steps, acceptance criteria, or repository/base assumptions that affect the contract.
- Approval is explicit, attributable, dated, tied to that exact revision, and preserved in `artifacts/request.md` plus an Approval evidence reference. Set `approved_revision`, `approved_by`, and `approved_at` only from that evidence. Generating a plan or receiving a bare command is not approval.
- A revised open plan stays open, records the approval blocker, and stops execution until reapproved. Status/receipt/link-only updates do not increment the scope revision or invalidate unchanged approval.
- Ready execution requires `approved_revision == scope_revision`, named approval evidence, satisfied/explicitly parallel-safe dependencies, and no execution blockers. Later external acceptance is not automatically an implementation blocker, but stays required for completion unless explicitly excepted.
- `Owner` is the default owner/final reviewer, not proof of an external assignee. Record actual system owners/reviewers when known; never invent a reviewer or request an author's own formal review.

After frontmatter/title, use exactly `## tldr-version` then `## agent-version`. Keep all detailed headings at level 3 or deeper inside the agent view.

### tldr-version — Only These Fields, In Order

1. **Scope:** concise implementation boundary.
2. **Status:** lifecycle/progress; essential blocker or completion qualification. Detailed evidence/limits stay in the agent view.
3. **Delivered:** one bullet per delivered statement, with direct Markdown links to its supporting commits **in every bullet when available**. A PR link supplements, never replaces, a known commit link. Use exact repository/IDs from authoritative receipts; map multi-repository claims to their own commits. Never invent links or treat planned work as delivered. If no commit is available, explicitly write `commit unavailable` or, for verified uncommitted work, `uncommitted`. If nothing is delivered, write `None yet.`
4. **Next:** a backtick-wrapped exact next primary command and resolved slug/request, followed by any prerequisite. Match the Resume command and response recommendation.
5. **Diagram:** optional fenced `mermaid` block, only when possible/useful and supported by evidence. Omit the field rather than invent architecture.

Use the template's bold field labels. No separate Summary, Evidence, Limits, Steps, Estimates, or other fields. Maximum **299 words**. Counting is deterministic: remove fenced Mermaid blocks including delimiters, replace inline Markdown links/images with their visible labels, then count remaining whitespace-separated tokens, including labels and non-diagram code. Formatting/list markers count conservatively as tokens. The [validator](scripts/validate_plan.py) implements this rule; a 300-token view fails.

### agent-version — Dense, Complete, Resumable

Use short technical statements, exact references, tables/checklists, and no duplicated receipts or empty ceremonial headings. No arbitrary length cap or Caveman dependency. Preserve precision, compatibility, security, and negative cases.

Required headings:

- `### Resume`: one current snapshot, completed/remaining work, active writer/run or none, checkpoint/blocker, essential evidence references, and `- Next: /plan-<command> <slug> — <gate>`. Never accumulate contradictory old “current” paragraphs.
- `### Scope`: goal/non-goals/compatibility, relevant risks/decisions, approval evidence/coverage, and publication permissions. Reference metadata rather than copying it repeatedly.
- `### Implementation`: dependency-ordered inline steps. Each names existing/new repository-relative files/symbols, expected behavior, negative cases, and acceptance. Keep landed work visible to avoid rebuilding it. Distinguish `landed`, `partially landed`, `planned`, and `blocked` from evidence, not old notes.
- `### Verification`: exact commands, working directories, prerequisites, expected results and acceptance mapping. Mark investigation-only baselines separately from feature acceptance. Unknown commands are a draft/readiness gap, not permission to invent results.
- `### History`: append-only `- YYYY-MM-DD /plan-command <slug>: result; evidence reference` per mutation. Do not reconstruct missing command history from filenames. Append factual corrections; never rewrite prior receipts.

Add Decisions/Dependencies/Execution/Outcome/Retrospective only when relevant. Keep detailed sanitized logs/screenshots in artifacts and link them; scope, stop conditions, and acceptance remain in `plan.md`. Preserve requests and evidence append-only. Estimates, architecture diagrams, rollback/operations and cross-project effects are proportional to the actual task, not mandatory filler.

## Evidence, Safety, And Completion

- Inspect owning code, schemas, neighboring tests, configuration, relevant history, and every affected repository boundary. Read local instructions. Source notes or an issue description alone do not prove behavior shipped.
- Check only relevant package manager/lockfile, working directory, CI/release runner, credentials/identity prerequisites, container entrypoint, runtime mocks, and local/remote documentation drift. Copy runnable commands from repository guidance.
- Record exact commands/tool calls and results, repository/base/tested commit, reviewer/CI state, deviations, and provenance. Copy opaque IDs and timestamps from authoritative output; distinguish approval, observation, and mutation times. Never reconstruct an ID or report an old snapshot as current.
- Never store/display secrets, copied secret-bearing chat, credential-bearing URLs/configuration, or secret environment values. Do not print raw `git remote -v`; use remote names (`git remote`) and read-only ref queries. Redact credentials before rendering any URL/output.
- Unavailable connectors/access are `unverified`, not passed/failed/clear. No interactive login during a read-only status query. Owner-reported testing without commands/scope stays Owner-reported, not independently rerun.
- A launched/completed agent run, local pass, merged PR, or contributor/license check is not whole-plan acceptance or build/test CI. Associate every result with the actual tested tree; compare landed content before reusing prior results and rerun invalidated checks.
- `done` requires every required implementation/acceptance criterion, required tests/real CI/reviews, current docs/config, and any promised issue/release/deployment evidence. Otherwise keep open. The Owner may explicitly accept a precisely scoped exception; preserve each unmet criterion, its exact waiver and residual external acceptance. No inherited exceptions or silent deletion of deferred scope.
- Local closure does not claim tracker closure, role enablement, live catalogs/cloud/devices, deployment, or downstream completion. A general “tested/approve done” does not waive those gates implicitly; ask a focused acceptance question when needed.
- Never self-merge, transition external work items, release, deploy, grant access, or clean/reset/force-push work merely to manufacture completion. Commit/push/draft-review only when the request or recorded publication permissions explicitly authorize them. Plan bookkeeping is not committed implicitly.

## Mutations, Moves, Index, And Concurrency

Reread current files before writing. Preserve unrelated edits and active writers; stop/rebase on concurrent changes rather than overwriting them. Scope/approval, both views, updated date, applicable receipts, append-only History and the selected index entry must agree after a mutation. Do not auto-run a suggested next command.

Initialize index sections: `Next`, `Open`, `Drafts`, `Blocked`, `Recently Done`, `Discarded`, `Unclassified Legacy Plans`, with `Plan prefix: plan` only for a new index lacking a configured prefix. One canonical link per plan, in its lifecycle section, containing title/ID, owner, update and concise blocker/next action. Blocked summaries do not duplicate canonical links. Preserve legacy entries and unrelated prose.

Before moving, check destination collisions, concurrent edits, and live incoming/outgoing Markdown/reference/wiki links under the configured root. Move the **complete bundle**; repair only live destinations and relative links, not historical quoted/code paths. Validate the selected bundle, its unique current index entry, and affected links after the move. For path-only repairs to other canonical plans, update their date and append path-only History without changing scope/approval. Legacy or otherwise unapproved edits require permission before the move; report the gate instead of silently rewriting them. Do not broadly normalize a vault.

The read-only validator checks structure, TL;DR size/fields, declared approval/readiness, bundle layout, index uniqueness and local link destinations. It does **not** prove consent, truthful delivery links, executed tests, CI success, Mermaid semantics, or safe agent behavior. Validate with `python3 <resolved-validator-path> --root "$PLAN_ROOT" --plan <slug>`; add `--ready` before execution. Resolve the validator relative to this contract's `scripts/` directory, not the working directory. Root-wide validation checks only v2 bundles; reports legacy content without rewriting it.

## Mandatory Next Command — Every Result

Every primary-command result and optional status result, including success, blocked, failed, unchanged, checkpoint and handoff, **must end with one explicit `Next:` line**. Use the exact command and actual resolved slug/request; include the gate, never just “continue”, an approval question, or a blocker. Missing root/target: ask for it, label necessary placeholders, and recommend a conditional rerun without guessing. This applies even when nothing was changed.

| Actual state | Next primary command |
| --- | --- |
| Draft needs investigation/revision/approval; changed open scope needs reapproval | `/plan-create <slug>` after the named decision/approval; open stays open |
| Approved, ready, no active writer | `/plan-execute <slug>` |
| Open, paused approved implementation remains, no active writer | `/plan-execute <slug>` after resume checks |
| Open, writer running or acceptance/check/review evidence pending | `/plan-sync <slug>` once the named evidence arrives; no duplicate execution |
| Done/discarded | `/plan-retro <slug>` |
| Retro edits proposed, not approved | `/plan-retro <selection>` after explicit approval |
| Retro complete, nothing remains | `/plan-create <new-request>` only when another task exists; label placeholder |

On mutations align TL;DR Next, Resume Next and final recommendation. Read-only results do not rewrite the stored recommendation. A suggestion never grants authority, bypasses a gate, starts another plan, or redispatches terminal work.
