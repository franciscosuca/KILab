# VS Code + Local Models: Why Copilot Chat Eats So Many Context Tokens

This folder documents how to run local models (via LM Studio) inside VS Code
Copilot Chat — and what that setup costs in context tokens:

- [setup-lmstudio-vscode-quickstart.md](setup-lmstudio-vscode-quickstart.md) —
  connect LM Studio to VS Code in 1 minute.
- [vscode-context-requirements.md](vscode-context-requirements.md) — how much
  context each chat mode actually needs.
- [issues/vscode-model-picker-tool-calling-findings.md](issues/vscode-model-picker-tool-calling-findings.md) —
  why `toolCalling: false` can hide a model from the picker entirely.
- [case-study/](case-study/) — two small-model failure cases analyzed from LM
  Studio logs.

The headline measurement, observed on a 30K-token local model
(Qwen2.5-Coder-1.5B via LM Studio):

| Bucket | Share of 30K window | ~Tokens |
|---|---|---|
| System Instructions | 14.4% | ~4,300 |
| Tool Definitions | 19.7% | ~5,900 |
| **Fixed overhead** | **34.1%** | **~10,200** |

Plus a "Reserved for response" slice, so roughly **half of the context window is
gone before the first user message**. The rest of this file explains where
those tokens go, cites the sources, and lists lower-overhead alternatives.

## Why the overhead is so large

- **A large system prompt** (~14%): agent role, output-format rules, safety
  instructions, workspace metadata, and every enabled instruction file are
  serialized into every request. See
  [vscode-context-requirements.md](vscode-context-requirements.md).
- **Tool schemas in every request** (~20%): with `toolCalling: true`, every
  enabled built-in tool and MCP server adds its full JSON Schema — roughly
  100–500 tokens per tool, capped at 128 tools per request. See
  [issues/vscode-model-picker-tool-calling-findings.md](issues/vscode-model-picker-tool-calling-findings.md).
- **No prefix caching on local servers**: LM Studio re-tokenizes the entire
  prefix on every turn, so the fixed ~10K tokens cost time again and again.
  See
  [case-study/case-qwen2.5-coder-1.5b-instruct-mlx.md](case-study/case-qwen2.5-coder-1.5b-instruct-mlx.md).
- **Small models amplify the ratio**: 10K tokens of scaffolding leaves little
  of a 16–32K window for your code, and sub-~3B models are unreliable at tool
  calling anyway. See
  [case-study/case-lfm2.5-vl-450m-heretic.md](case-study/case-lfm2.5-vl-450m-heretic.md).

## How to reduce it inside VS Code

- **Do not treat `toolCalling: false` as a reliable Ask/Edit workaround.** It
  drops the tool block, but in the current observed VS Code build it can also
  remove the model from the chat picker entirely. See
  [issues/vscode-model-picker-tool-calling-findings.md](issues/vscode-model-picker-tool-calling-findings.md).
- **Trim the tool picker**: *Configure Tools* in the chat input — enable only
  the handful of tools the task needs instead of all built-ins + MCP servers.
- **Disable unused MCP servers** (`MCP: List Servers` -> Disable) — each one
  injects its full tool manifest.
- **Shrink instruction files**: keep `.github/copilot-instructions.md` and
  prompt files short; they are sent verbatim every turn.
- **Compact the conversation** before the window fills (the button in the
  session-info popover) so old turns stop competing with the fixed overhead.

## Lower-overhead harness alternatives

If the fixed VS Code/Copilot prefix is leaving too little room for code, consider
changing the harness rather than only trimming VS Code settings. The repository
root's [harness comparison](../../../harness.md) is a compact reference to
CLI-first and hybrid options—Pi, Hermes Agent, OpenClaw, Continue, and GitHub
Copilot—with rough prompt-overhead ranges, BYOK details, and LM Studio
compatibility. CLI-first tools generally expose a smaller, more configurable
system prompt, leaving more of a local model's context window for the task.

## Sources

- [VS Code Docs — Use tools with agents](https://code.visualstudio.com/docs/agents/run/tools)
  (tool selection, 128-tool limit)
- [VS Code Docs — Add and manage MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
  (each server's tools are injected into chat)
- [Anthropic Engineering — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
  (tool definitions overloading context; 150K -> 2K token reduction)
- [Cloudflare Blog — Code Mode](https://blog.cloudflare.com/code-mode/)
  (independent confirmation of the same finding)
- Local measurements: Session Info popover in VS Code Chat against LM Studio
  (screenshots in this guide's history: 13.1K/30K used with an empty request).
