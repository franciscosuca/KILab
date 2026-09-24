# Blind Test Workflow (Two-Agent Pattern)

This workflow mirrors the pattern: one model writes tests, a different model implements without seeing them.

## Is A2A required?

No. You can run this with regular agent modes and clear handoff boundaries.

Use A2A only if you need:
- cross-tool orchestration between separate external agents/services
- audit trails and structured agent-to-agent contracts
- centralized policy enforcement across many repos

For one repository, agent modes plus process discipline are usually enough.

## Recommended Workflow

1. Run `test-oracle` with only requirements.
2. Let it write failing tests plus an acceptance checklist.
3. Start a separate `blind-implementer` run.
4. Give only requirement text and checklist, never test files.
5. Let it code and run tests, but forbid opening test sources.
6. Final gate: rerun full tests with `test-oracle`.

## Practical Guardrails

- Keep tests in predictable paths (`tests/`, `__tests__/`, `*.spec.ts`, `*.test.tsx`).
- In `blind-implementer`, treat those paths as forbidden.
- Use separate chat turns or sessions for each agent role.
- Handoff only behavior-focused acceptance bullets.

## Example Prompt Sequence

### Prompt A (to test-oracle)

"Feature: add a retry button to failed invoice payment. Requirements:
- show retry only when status is failed
- retry disabled while request is in flight
- success state replaces retry with receipt link
- error state keeps retry visible and shows toast
Write robust tests and a short acceptance checklist."

### Prompt B (to blind-implementer)

"Implement this feature from requirements only. Do not read tests.
Acceptance checklist:
- Retry button only on failed payment
- Disabled during in-flight retry
- Receipt link appears on success
- Retry remains with error toast on failure"

### Prompt C (to test-oracle)

"Run and evaluate tests, report failures by behavior category, and list any missing edge cases."

## Example in this repo

- Source agent: `coding-agent-pack/catalog/core/agents/test-oracle.md`
- Source agent: `coding-agent-pack/catalog/core/agents/blind-implementer.md`

Install them into a target project's Copilot directory with:

```bash
coding-agent-pack/scripts/install-pack.sh --target . --harness copilot --agents test-oracle,blind-implementer --skills none
```

Review the generated files in `.github/agents/` and adapt language/framework details as needed.
