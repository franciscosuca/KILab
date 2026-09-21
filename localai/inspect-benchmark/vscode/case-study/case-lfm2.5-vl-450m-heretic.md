# Case Study: LFM2.5-VL-450M Fails Instantly with "failed to parse grammar"

**Date:** 2026-09-17
**Setup:** VS Code Copilot Chat (agent mode) -> LM Studio server
(`http://127.0.0.1:1234`) -> `lfm2.5-vl-450m-heretic`,
context length 128,000, `toolCalling: true` in `chatLanguageModels.json`.
**Task given to the model:** "give me a summary about this file" — a trivial
read-and-summarize request.

## What happened (TL;DR)

The request **never reached the model's sampler**. LM Studio's MLX engine
rejected it with HTTP 400 *before generating a single token*:

```text
Engine protocol predict request returned 400:
{"error":{"code":400,"message":"Failed to initialize samplers:
failed to parse grammar","type":"invalid_request_error"}}
```

VS Code surfaced this as "Sorry, your request failed. Please try again."
Retrying changed nothing — the same request failed identically at
**08:20:28, 08:41:18, 08:41:55, and 08:42:28**. Unlike the Qwen case (a slow
loop), this failure is instant, deterministic, and 100% reproducible.

## The log evidence

Source: `~/.lmstudio/server-logs/2026-09/2026-09-17.1.log`.

### 1. The failure: sampler initialization dies on grammar parsing

```text
[2026-09-17 08:20:28][lfm2.5-vl-450m-heretic] Running chat completion on conversation with 3 messages.
[2026-09-17 08:20:28][lfm2.5-vl-450m-heretic] Streaming response...
[2026-09-17 08:20:28][ERROR][lfm2.5-vl-450m-heretic] Engine protocol predict
  request returned 400: {"error":{"code":400,"message":"Failed to initialize
  samplers: failed to parse grammar","type":"invalid_request_error"}}.
```

Note the timeline: request received, streaming started, error returned — all
**within the same second**. There is no "Prompt processing progress" line at
all. The engine rejects the request during setup, not during generation.

### 2. Retries are futile — same input, same instant 400

```text
[2026-09-17 08:41:18] Running chat completion on conversation with 3 messages.
[2026-09-17 08:41:18][ERROR] ... "Failed to initialize samplers: failed to parse grammar" ...
[2026-09-17 08:41:55] Running chat completion on conversation with 3 messages.
[2026-09-17 08:41:55][ERROR] ... "Failed to initialize samplers: failed to parse grammar" ...
[2026-09-17 08:42:28] Running chat completion on conversation with 3 messages.
[2026-09-17 08:42:28][ERROR] ... "Failed to initialize samplers: failed to parse grammar" ...
```

Always exactly **3 messages** (system + user + priming), always the same error.
This rules out context size as the trigger: the failure happens at 3 messages
on a 128K window.

### 3. The control experiment: the same model works without tools

Earlier the same day, the **same model** answered successfully:

```text
[2026-09-17 07:54:52][lfm2.5-vl-450m-heretic] Running chat completion on conversation with 3 messages.
[2026-09-17 07:54:52] Prompt processing progress: 0.0%
...
[2026-09-17 07:54:56] Finished streaming response
```

Four seconds, no error. The difference between the working and failing requests
is not the model, the message count, or the context length — it is **what the
client attached to the request**: VS Code's agent-mode payload with
`toolCalling: true`.

## Root cause

**VS Code sends a tool-calling grammar that the MLX engine cannot compile for
this model.**

When `toolCalling: true` is configured, each request carries JSON Schemas for
every enabled tool. LM Studio converts those schemas into a **grammar** (a
constrained-decoding specification) so the model's output can be parsed as
valid tool calls. For `lfm2.5-vl-450m-heretic` — a 450M-parameter
vision-language MLX build — the grammar compiler fails
("failed to parse grammar"), sampler initialization aborts, and the engine
returns 400 before any token is generated.

Why this model specifically:

1. **The grammar is too large/complex for this engine+model combo.** A full
   VS Code tool manifest is a big schema; grammars that larger chat-template-
   complete models accept can exceed what this small experimental MLX build's
   sampler stack supports.
2. **It is a 450M "heretic" (abliterated) VL model** — an experimental
   community build, not a tool-calling-tuned model. Even if the grammar had
   parsed, a 450M model cannot use ~100 tools meaningfully.
3. **The error is deterministic**, so every VS Code retry hits the same wall.
   No amount of "Try Again" fixes a request that is malformed for this engine.

## Parallels with the Qwen2.5-Coder-1.5B case

Both failures, from the same morning on the same machine, share **one root
cause**: sending the full agent-mode tool surface to a model that is far too
small for it. They differ only in *where* the failure surfaces:

| | [case-qwen2.5-coder-1.5b-instruct-mlx.md](case-qwen2.5-coder-1.5b-instruct-mlx.md) | this case |
|---|---|---|
| Model size | 1.5B | 450M |
| Grammar accepted? | Yes | **No — 400 at sampler init** |
| Failure mode | Runtime: infinite tool-call loop until compaction, ~9 min, ~20 requests | Protocol: instant, deterministic 400, 0 tokens generated |
| User experience | Slow, silent, wastes minutes and compute | Fast, visible, but confusing ("try again" never helps) |
| Trigger | `toolCalling: true` on a tiny model | `toolCalling: true` on a tinier model |
| Task needed tools? | No (simple question) | No (summarize one file) |

The shared lesson: **the fixed agent-mode overhead is not just wasteful (tokens,
latency) — for small models it is the difference between working and not
working.** Qwen accepted the grammar and drowned in it at runtime; LFM could
not even parse it. Both tasks would have succeeded in plain chat mode.

## How to avoid this

- **Do not rely on `toolCalling: false` as an Ask/Edit workaround.** It removes
  the grammar from the request, but in the current observed VS Code build it
  also removes the model from the picker. Use LM Studio Chat or another
  chat-first client for this 450M model instead.
- **Do not retry on this error.** `failed to parse grammar` is deterministic;
  retrying the identical request always fails. Change the configuration, not
  the luck.
- **Match the model to the mode:** experimental/abliterated VL builds are for
  bare chat experiments, not agent mode. Use tool-calling-tuned models
  (>= ~7B) for Agent mode.
- **Sanity-check new models in LM Studio's own Chat tab first** (no tools, no
  grammar). If it works there but fails in VS Code, the tool payload is the
  suspect — this A/B takes under a minute.

## Related

- [case-qwen2.5-coder-1.5b-instruct-mlx.md](case-qwen2.5-coder-1.5b-instruct-mlx.md) —
  the sibling failure: grammar accepted, looped instead.
- [../README.md](../README.md) —
  what the tool payload contains and what it costs.
- [../issues/vscode-model-picker-tool-calling-findings.md](../issues/vscode-model-picker-tool-calling-findings.md) —
  why disabling tool calling does not reliably expose an Ask-only model.
