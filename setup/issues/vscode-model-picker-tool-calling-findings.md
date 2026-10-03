# Finding: VS Code Model Picker and Tool-Calling Capability

**Observed:** 2026-09-17, VS Code Stable with a custom LM Studio endpoint configured in `chatLanguageModels.json`.

## Finding

In the current observed VS Code build, `toolCalling` is more than a request-size setting. It also acts as a capability or eligibility signal for custom chat models:

| Configuration | Request behavior | Observed picker behavior |
|---|---|---|
| `"toolCalling": true` | VS Code can attach tool schemas and tool-calling grammar | The model remains available for chat and agent-backed flows |
| `"toolCalling": false` | Tool schemas are not attached | The model can disappear from the chat model picker entirely |

Therefore, setting `toolCalling` to `false` is **not** a reliable way to make a model Ask/Edit-only. It reduces the request payload, but it can also make the model unusable from VS Code Chat. The exact Ask-mode eligibility behavior is implementation-dependent; the picker result above is the behavior observed in this setup.

This matches the documented constraint that models used with VS Code agents must support tool calling, but the documentation does not make `toolCalling: false` a general Ask-mode configuration switch:

- [VS Code: Language model configuration](https://code.visualstudio.com/docs/agent-customization/language-models)
- [VS Code: Use tools with agents](https://code.visualstudio.com/docs/agents/run/tools)

## Evidence from the local tests

- `qwen2.5-coder-1.5b-instruct-mlx` with `toolCalling: true` accepted the request but repeatedly emitted tool calls until VS Code compacted the conversation. See [case-qwen2.5-coder-1.5b-instruct-mlx.md](case-study/case-qwen2.5-coder-1.5b-instruct-mlx.md).
- `lfm2.5-vl-450m-heretic` with `toolCalling: true` failed immediately in LM Studio with `failed to parse grammar`. The same model answered in LM Studio Chat without the tool payload. See [case-lfm2.5-vl-450m-heretic.md](case-study/case-lfm2.5-vl-450m-heretic.md).
- Changing `toolCalling` to `false` removed the tool payload, but the model was no longer available in the VS Code model picker in the observed setup.

These results separate two questions that were previously conflated:

1. **Can the model handle a tool payload?** The Qwen and LFM tests show that small local models may loop or fail before generation.
2. **Can VS Code expose a non-tool model in Chat?** In this setup, disabling tool calling did not expose an Ask-only model; it removed the model from the picker.

## Practical configuration choices

- For a model that must remain selectable in VS Code Agent mode, use `toolCalling: true`, a tool-calling-capable model, and a small enabled-tool set. A larger model is appropriate for agent workflows.
- For a small or non-tool-calling model, use LM Studio Chat or another chat-first client such as Continue, Cline, Roo Code, or Open WebUI. These clients can use the model without requiring VS Code's agent tool surface.
- Treat a model disappearing after changing `toolCalling` as an eligibility or picker issue, not proof that the endpoint is down. Compare the model configuration and test the same endpoint in LM Studio Chat.

The safe conclusion is: **disabling tool calling can reduce overhead, but in the observed VS Code configuration it is not a usable Ask-mode workaround.**
