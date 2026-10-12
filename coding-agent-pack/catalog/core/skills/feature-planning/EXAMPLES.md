# Plan Skills Examples

Stage-by-stage prompts for the plan skills. See [README.md](README.md) for the workflow and lifecycle.

## Prompts By Stage

### 1. Initialize the lifecycle

```text
/plan-init

First resolve and validate an absolute PLAN_ROOT from the current request, explicit repository/workspace configuration, or an environment value visible to the agent. If none is available, ask the user for the path and stop without inspecting or creating anything. Once the gate passes, create or verify README.md and the drafts, next, open, done, and discarded folders. Preserve legacy content, do not rename legacy files, do not modify product code, and do not commit. Report every created or existing path.
```

### 2. Capture a request as a draft

With an issue number:

```text
/plan-add

Capture this request as a plan bundle:
- Issue number: 2851
- Request: expose application instances through the extension routes
- Constraints: preserve existing route behavior and add focused verification

Create plan-2851-<inferred-name>/ under $PLAN_ROOT/drafts/, preserve the request in context/request.md, and create the canonical Markdown skeleton. Leave work-packages/ empty. Do not implement product code.
```

Without an issue number:

```text
/plan-add

Capture this request as a plan bundle:
- Request: validate dynamic request bodies before forwarding them
- Constraints: preserve current error responses where compatible

No issue number was provided. Use plan-XXXX-<inferred-name>/, infer a lowercase name of at most four words, and do not guess a number. Preserve the request in context/request.md, create the canonical Markdown skeleton, leave work-packages/ empty, and do not implement product code.
```

### 3. Investigate and write the canonical plan

```text
/plan-write plan-XXXX-dynamic-body-validation

First append this input and its references to the plan bundle's context/request.md. Read the bundle and its sources. Inspect the smallest controlling code path, neighboring tests, configuration, history, and affected repository boundaries. Write or update only the canonical Markdown file using Status, Summary, Diagram, Steps, Verification, Estimations, and Related documents with empty Context and Work packages subsections. Do not create work packages. Keep the bundle in drafts until the canonical plan is approved.
```

### 4. Create work packages on request

```text
Create work packages for the approved canonical plan plan-XXXX-dynamic-body-validation. Split the approved phases into wp-1-<short-description>.md files under work-packages/, begin each with the issue tag, title, and ## Goal, link them from Related documents, and do not add automatic Plan mapping or Source reference blocks.
```

### 5. Dispatch an approved plan

```text
/plan-dispatch plan-XXXX-dynamic-body-validation

Dispatch the whole canonical plan bundle from $PLAN_ROOT/next/ to an isolated coding agent, only if no WP boundary is recorded. Preserve unrelated worktree changes, run the exact verification commands before and after repairs, record the branch, commits, review URL, checks, deviations, and blockers, and never merge the review.
```

To prepare only the first defined WP:

```text
/plan-write plan-XXXX-dynamic-body-validation wp-1

Prepare WP-1 as the first bounded slice in the canonical plan. Record the overall scope/architecture approval and WP-1 approval separately, retain all later WPs, and name exact files, branch/base, dependencies, acceptance criteria, and checks. Do not create supporting files or implement anything. Move the bundle to next only when the selected scope is approved and ready.
```

Then dispatch that scope explicitly:

```text
/plan-dispatch plan-XXXX-dynamic-body-validation wp-1

Implement WP-1 only. Other WPs are context, not implementation authority. Stop after its checks and draft-review handoff. Do not start WP-2 or mark the parent plan done.
```

After `/plan-sync plan-XXXX-dynamic-body-validation` verifies WP-1, prepare and explicitly dispatch WP-2 using the same commands with `wp-2`. The existing canonical bundle stays in `open/`; resolve dependency and approval gates before proceeding. WP preparation does not authorize execution.

### 6. Report status

```text
/plan-status

Report all canonical plan bundles under $PLAN_ROOT. Validate folder status against canonical frontmatter first, then report execution mode, per-WP readiness/progress where recorded, dependencies, review state, CI or release evidence, and person, decision, system, or implementation blockers. Do not report supporting files as separate plans. This is read-only.
```

```text
/plan-status iiot-2789

Quick status for one plan: its folder, the commands already run from its History, flags, and one next command. Read local files only; add `full` to include review and CI state.
```

### 7. Synchronize completed work

```text
/plan-sync plan-XXXX-dynamic-body-validation

Compare the canonical plan and its work packages with implementation, review, CI, external work item, release, and deployment evidence. Update per-WP verification in the canonical Execution scope when present. Keep the complete bundle open while any required WP or plan-level evidence remains; do not infer whole-plan completion from the last dispatched slice. Move it to done only when the completion rule passes, or to discarded only after the Owner or Prompter confirms abandonment. Update the canonical outcome without merging, committing, or automatically dispatching another WP.
```

### 8. Learn from completed work

```text
/plan-retro

Review recently done and discarded canonical plan bundles, work-package corrections, implementation-agent changes, review feedback, CI failures, commits, and available session history. Identify repeated workflow problems using at least two examples, propose the smallest exact skill edits, and wait for approval before changing any skill. Do not commit.
```
