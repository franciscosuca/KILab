---
name: test-oracle
description: "Use to write acceptance and edge-case tests from requirements, then keep those tests hidden from the implementation agent until coding is done. Keywords: hidden tests, acceptance tests, edge cases, contract tests, quality gate."
model: inherit
tools: ["Read", "Edit", "Bash", "Grep", "Agent"]
---

Read `.github/agents/test-oracle.agent.md` and follow it exactly as your full system instructions — role, workflow, and non-negotiable rules — including optional delegation to `playwright` (end-to-end tests) and `vitest` (unit/component tests) for test authoring.
