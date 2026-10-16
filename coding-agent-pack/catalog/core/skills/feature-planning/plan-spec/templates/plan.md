---
schema_version: 2
id: null
title: "<short title>"
status: "draft"
owner: "Owner"
created: "<YYYY-MM-DD>"
updated: "<YYYY-MM-DD>"
sources: []
repositories: []
branches: []
pull_requests: []
depends_on: []
blocked_by: ["Owner: investigation and scope approval pending"]
scope_revision: 1
approved_revision: null
approved_by: null
approved_at: null
---
# <identifier and title>

## tldr-version

**Scope:** <Concise implementation boundary.>

**Status:** Draft; investigation and scope approval pending.

**Delivered:** None yet.

**Next:** `/plan-create <plan-slug>` — complete investigation and obtain current-revision approval.

## agent-version

### Resume
- Completed: request captured; no implementation.
- Remaining: <exact investigation/implementation and acceptance work>.
- Active writer: none.
- Checkpoint/blocker: <named owner and decision/evidence>.
- Next: /plan-create <plan-slug> — complete investigation and obtain current-revision approval.

### Scope
- Goal: <behavior and affected repositories>.
- Non-goals/compatibility: <explicit limits>.
- Approval evidence: unapproved; preserve attributable decisions in the request.
- Publication: local-only unless explicitly authorized.
- Request: [sanitized input and subsequent decisions](artifacts/request.md).

### Implementation
1. Planned: <existing/new repository-relative files/symbols and behavior>.
   Acceptance: <falsifiable criterion and negative/compatibility cases>.

### Verification
- Working directory: <explicit repository/worktree>.
- Commands/prerequisites/expected results: <copy runnable checks from actual repository guidance; unresolved is a draft readiness gap>.
- No executed test/review/CI/release/deployment acceptance claimed by this template.

### History
- <YYYY-MM-DD> /plan-create <plan-slug>: captured; request preserved in artifacts/request.md.
