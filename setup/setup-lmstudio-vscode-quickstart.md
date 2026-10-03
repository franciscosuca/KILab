# LM Studio + VS Code Copilot Chat

## 1. LM Studio

1. Load your model.
2. **Developer** tab -> **Start Server** (default port `1234`).
3. Set **Context Length** to a value your RAM can hold — see
   [../context-window-hardware.md](../context-window-hardware.md). Enable
   **Flash Attention**.
4. Verify: `curl http://127.0.0.1:1234/v1/models` and copy the exact `id`.

## 2. VS Code

1. Chat model picker -> **Manage Language Models** -> **Add Models** ->
   **Custom Endpoint** -> API type **Chat Completions**.
2. VS Code opens `chatLanguageModels.json`. Set:

```json
[
  {
    "name": "LM Studio",
    "vendor": "customendpoint",
    "apiKey": "${input:lmStudioApiKey}",
    "apiType": "chat-completions",
    "models": [
      {
        "id": "google/gemma-4-26b-a4b-qat",
        "name": "google/gemma-4-26b-a4b-qat",
        "url": "http://127.0.0.1:1234",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 64000,
        "maxOutputTokens": 64000
      },
      {
        "id": "qwen2.5-coder-1.5b-instruct-mlx",
        "name": "qwen2.5-coder-1.5b-instruct-mlx",
        "url": "http://127.0.0.1:1234",
        "toolCalling": true,
        "vision": false,
        "maxInputTokens": 16000,
        "maxOutputTokens": 14000
      }
    ]
  }
]
```

## Constraints that bite (learned the hard way)

- `maxInputTokens + maxOutputTokens` **must not exceed** the context length
  loaded in LM Studio. Claiming 128k+128k against a 64k server fails.
  `toolCalling: true` sends **all enabled tools** (built-in + MCP servers) in
  every request — with ~99 tools that alone can blow the budget and cause
  `No lowest priority node found (path: eie)`. Use it only with a
  tool-calling-capable model and trim the tool picker to a few tools.
- `toolCalling: false` removes the tool payload, but in the current observed
  VS Code build it can also hide the model from the model picker rather than
  expose it as Ask/Edit-only. Use a chat-first client for small models that do
  not support tools; see
  [issues/vscode-model-picker-tool-calling-findings.md](issues/vscode-model-picker-tool-calling-findings.md).
- Models under ~3B parameters are not useful for Agent mode regardless of
  configuration.
- Full details: [vscode-context-requirements.md](vscode-context-requirements.md).
