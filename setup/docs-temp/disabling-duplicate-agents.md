# Avoiding Duplicate Agents in the Agent Picker

The coding-agent-pack keeps one source definition under `coding-agent-pack/catalog/core/` and can generate native projections for multiple harnesses:

- **GitHub Copilot / VS Code**: `.github/agents/*.agent.md`
- **Claude Code**: `.claude/agents/*.md`

If both surfaces are installed in the same repository and editor, the same logical agent can appear twice in the picker. Install only the harnesses you use, or disable one surface locally.

## GitHub Copilot / VS Code agents

Control visibility and delegation through agent frontmatter:

| Flag | Default | Effect |
|---|---|---|
| `user-invocable: false` | `true` | Hides the agent from the manual picker while allowing delegation. |
| `disable-model-invocation: true` | `false` | Prevents other agents from invoking it. |

To fully disable an agent:

```yaml
---
name: "playwright"
user-invocable: false
disable-model-invocation: true
---
```

Or omit that agent from the installer selection:

```bash
coding-agent-pack/scripts/install-pack.sh \
  --harness copilot \
  --agents test-oracle,blind-implementer
```

## Claude Code agents

Claude Code can block specific agents through settings:

```json
{
  "permissions": {
    "deny": ["Agent(playwright)", "Agent(vitest)"]
  }
}
```

For a personal-only override, use `.claude/settings.local.json` rather than committing the setting.

## Recommended practice

Treat `coding-agent-pack/catalog/core/` as the source of truth. Do not manually edit generated `.github/agents` or `.claude/agents` files; change the source and rerun the installer instead. Archived definitions are not installed automatically.
