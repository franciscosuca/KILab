# How Much Context VS Code Copilot Chat Requires

What we verified experimentally (2026-09, VS Code Stable + local LM Studio
models) plus the official
[model configuration reference](https://code.visualstudio.com/docs/agent-customization/language-models#_model-configuration-reference).

## How VS Code computes the budget

- VS Code trusts only `chatLanguageModels.json`: it treats
  `maxInputTokens + maxOutputTokens` as the model's total context window. The
  official docs state the sum **must not exceed** the model's real context
  window.
- The LM Studio context slider is invisible to VS Code. If you claim 128k in
  VS Code but the server is set to 64k, LM Studio hard-truncates and responses
  degrade or fail.
- VS Code builds each request as a prioritized element tree (system prompt,
  tool schemas, workspace context, user message). If it does not fit the
  budget, lowest-priority elements are pruned. When nothing prunable remains,
  the request fails with:

  ```text
  No lowest priority node found (path: eie)
  ```

## Token requirements by mode (@thesis)

There is no published numeric minimum; these are the practical floors we
observed:

| Mode | What is injected | Practical minimum `maxInputTokens` |
| --- | --- | --- |
| Ask | System prompt + your message + attachments | ~4k |
| Edit | Ask + edit-tool instructions + file context | ~8k |
| Agent, no extra tools | System prompt + base tool schemas (~5-10k tokens) | ~16k |
| Agent, many tools | Add ~200-1,000+ tokens per enabled tool; 99 tools (built-in + MCP servers) can exceed 20k-40k | 32k-64k |

Consequences:

- `toolCalling: false` removes tool-schema overhead and prevents Agent-mode
  tool requests, but in the current observed VS Code build it can also hide
  the model from the picker entirely. It is not a reliable Ask-only switch;
  for models under ~3B parameters, use a chat-first client unless your build
  still exposes the model. See
  [issues/vscode-model-picker-tool-calling-findings.md](issues/vscode-model-picker-tool-calling-findings.md).
- `toolCalling: true` sends **every** tool enabled in the Configure Tools
  picker (built-ins plus MCP servers like GitHub/Figma/Miro) on each request.
  Trim the selection to a handful of tools for small local models.

## Configuration rules that avoid the failure (@thesis)

1. `maxInputTokens + maxOutputTokens <=` the context length actually loaded in
   LM Studio.
2. Leave headroom: `maxInputTokens` = loaded context minus
   `maxOutputTokens` (e.g. 64k loaded -> 60000 input / 4000 output).
3. Do not copy the model card's maximum context into VS Code unless you
   validated the KV cache fits your RAM — see
   [../context-window-hardware.md](../context-window-hardware.md).
4. If you still hit `no lowest priority node found`: reduce enabled tools,
   lower `maxOutputTokens`, or raise the LM Studio context slider (and the VS
     Code values to match).
