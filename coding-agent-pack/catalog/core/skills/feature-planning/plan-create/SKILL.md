---
name: plan-create
description: "Create or revise a feature-planning v2 plan: initialize an explicitly configured root, capture the request, investigate real sources, and prepare an approved two-view implementation contract. Does not implement product changes."
argument-hint: "<request, plan slug, or issue key> [revision or explicit approval]"
user-invocable: true
---

# Create Or Revise A Plan

Read the [shared contract](../plan-spec/SKILL.md) first. Pass its explicit absolute `PLAN_ROOT` gate before reading/scanning plan data or investigating this lifecycle task. Missing/invalid root: ask and stop, with a conditional `Next:` command. This command plans; it does not implement product code, create branches, commit, or publish.

## Procedure

1. **Initialize only the selected root.** After the gate, inventory existing content. Add missing lifecycle folders/index sections idempotently; preserve existing prose, prefix, legacy entries and unrelated plans. Do not overwrite a non-empty index or classify/move legacy content automatically.
2. **Select one request/bundle.** Search all lifecycle folders for an existing slug/issue/distinctive request before creating. Ask on ambiguity/collision. Existing v2 draft/next/open bundles may be revised; open stays open. Terminal/legacy bundles remain read-only unless explicit migration or new rework scope is agreed. Never infer a missing issue number.
3. **Capture before summarizing.** Create only `plan.md` and `artifacts/`, preserving the sanitized request/examples/constraints/references in `artifacts/request.md`. Append subsequent inputs/approval evidence, never overwrite earlier entries. Add supporting artifacts only when they reduce repeated investigation; no shadow implementation plans.
4. **Investigate.** Read affected repositories' instructions, smallest controlling implementation, schemas, adjacent tests, configuration, relevant commits/blame and cited remote issue/docs when available. Trace relevant service/client/persistence/auth/deployment/documentation boundaries. Mark reached/unavailable sources. Classify actual work as landed, partially landed, planned or blocked; do not rebuild landed prerequisites or treat old plans as current evidence.
5. **Resolve evidence-backed choices.** Ask only for product/architecture/access decisions evidence cannot answer. Name dependency owners, compatibility/security/negative cases, and exact verification commands/working directories/prerequisites. Fixture construction is implementation work when authoritative source exists, not automatically an Owner prerequisite. Distinguish execution blockers from later acceptance gates.
6. **Write both views.** Use the contract's template and metadata. TL;DR has only Scope, Status, Delivered with per-claim commit links when available, Next, and optional Diagram; maximum 299 words excluding diagrams. Put exact files/symbols, inline steps/acceptance, verification, decisions/non-goals and resume/checkpoint details in the agent view. Preserve prior execution/Outcome/History; do not create work-package or workflow documents.
7. **Bind approval.** Record only explicit, attributable approval of the current `scope_revision`. A generated plan or bare “continue” is not approval of unspecified changes. Increment revision for material contract changes, retaining prior approval as historical; stop execution until current revision is approved. Evidence/status/link-only refreshes preserve the revision.
8. **Apply readiness.** A first plan stays in drafts while material decisions/readiness/approval are missing. When current scope is approved and ready, move the complete draft bundle to next, repairing authorized live links/index. A next plan that loses readiness is not executable; flag it and agree the correction rather than hiding blockers. An open revision stays open with an explicit gate until reapproved. Never erase deferred work to pass readiness.
9. **Validate/persist.** Reread to detect concurrent changes. Refresh both views, `updated`, concise append-only History and one index entry. Check structure/word count/links with the contract's read-only validator; use `--ready` for a prepared plan. Do not claim future acceptance tests passed during planning. If a gate remains, record it accurately instead of pretending the document is execution-ready.

## Result And Next Command

Return selected path, scope revision/approval, changed/created bookkeeping, reached evidence, blockers and state. Every result—including failed, blocked, unchanged, checkpoint and handoff—must end with one `Next:` line from the shared contract.

- Ready: `Next: /plan-execute <actual-slug> — approved revision and readiness verified.`
- Needs revision/approval: `Next: /plan-create <actual-slug> — after <named decision/approval>.`
- Root/target unknown: ask for it; show the conditional command with a clearly labeled placeholder, never a guessed path/ID.

Align stored TL;DR/Resume Next with the recommendation when mutating. Suggest only; never execute the next command automatically.
