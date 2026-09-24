# .claude

Claude Code configuration for this repository.

## Commands

Invoke with `/project:<command-name>` in Claude Code (CLI or VS Code).

| Command | Purpose |
|---------|---------|
| `implementation-plan` | Create a concise 3-section implementation plan (pre-requisites, files, steps) |
| `protocol-integration-planner` | Plan and scope a new IIoT protocol integration with effort estimates and Jira tickets |
| `react-minor-changes` | Apply small React/TypeScript changes safely with a concise summary |
| `release-check` | Run local quality gates (lint, test, build) before publishing |
| `vitest-setup` | Bootstrap or maintain a Vitest unit/component test suite |

## Hooks

Hooks run automatically on Claude Code lifecycle events.

| Event | Script | Behavior |
|-------|--------|----------|
| `Stop` | `hooks/release-check.sh` | Blocks completion (exit 2) if lint/test/build fail; Claude must fix before finishing |

### How it works

- **Exit 0** → checks pass, Claude completes normally
- **Exit 2** → checks fail, Claude is forced to continue and fix issues
- **Loop guard** → if already re-triggered (`stop_hook_active`), exits cleanly to avoid infinite loops

### Requirements

- Project must have `lint`, `test`, or `build` scripts in `package.json` (missing scripts are skipped)

## Usage

```bash
# Manual command invocation in Claude Code
/project:release-check

# Hook fires automatically — no action needed
```
