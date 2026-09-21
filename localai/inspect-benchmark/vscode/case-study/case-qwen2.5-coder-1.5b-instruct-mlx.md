# Case Study: Qwen2.5-Coder-1.5B Loops Until Compaction, Never Answers

**Date:** 2026-09-17
**Setup:** VS Code Copilot Chat (agent mode) -> LM Studio server
(`http://127.0.0.1:1234`) -> `qwen2.5-coder-1.5b-instruct-mlx`,
context length 32,000, `toolCalling: true` in `chatLanguageModels.json`.
**Task given to the model:** a simple question — no edits, no multi-step work
required.

## What happened (TL;DR)

One simple question turned into a **~9-minute, ~20-request agent loop**. The
model kept emitting tool calls instead of a final answer. Each round-trip added
2 messages to the conversation until the context window filled, VS Code
**compacted the conversation** (39 -> 17 messages), the loop restarted from the
summary, and the user finally cancelled. The task was never completed.

```text
08:20:49  3 messages   first request — prompt processing alone takes 27 s
08:21:19  5 messages   model answers with a tool call, not a final answer
08:21:22  7 messages   ... and again ...
   ...    +2 messages every ~3 s — the agent loop is spinning
08:26:15  39 messages  context nearly full; one turn now takes 2m23s
08:28:47  17 messages  VS Code COMPACTED the conversation; loop restarts
08:29:21  20 messages  loop resumes on top of the summary
08:29:46  —            "Client disconnected" — user gives up
```

## The log evidence

Source: `~/.lmstudio/server-logs/2026-09/2026-09-17.1.log`.

### 1. The first request: 27 seconds of prompt processing before token one

```text
[2026-09-17 08:20:49] Running chat completion on conversation with 3 messages.
[2026-09-17 08:20:53] Prompt processing progress: 18.0%
[2026-09-17 08:20:58] Prompt processing progress: 35.9%
[2026-09-17 08:21:02] Prompt processing progress: 53.9%
[2026-09-17 08:21:07] Prompt processing progress: 71.9%
[2026-09-17 08:21:12] Prompt processing progress: 89.8%
[2026-09-17 08:21:16] Prompt processing progress: 100.0%
[2026-09-17 08:21:19] Finished streaming response
```

Only 3 messages (system prompt + user question + priming), yet prompt
processing needs **27 seconds**. That is the fixed overhead described in
[../README.md](../README.md):
~10K tokens of system instructions + tool schemas, reprocessed on **every**
request because there is no prefix caching.

### 2. The loop: +2 messages every ~3 seconds

```text
[2026-09-17 08:21:19] Running chat completion on conversation with 5 messages.
[2026-09-17 08:21:22] Running chat completion on conversation with 7 messages.
[2026-09-17 08:21:26] Running chat completion on conversation with 9 messages.
[2026-09-17 08:21:29] Running chat completion on conversation with 11 messages.
...
[2026-09-17 08:21:55] Running chat completion on conversation with 27 messages.
[2026-09-17 08:21:59] Running chat completion on conversation with 29 messages.
...
[2026-09-17 08:22:50] Running chat completion on conversation with 35 messages.
[2026-09-17 08:22:57] Running chat completion on conversation with 37 messages.
[2026-09-17 08:26:15] Running chat completion on conversation with 39 messages.
```

This is the signature of an agent that **never decides it is done**: each
response is another tool call (+1 assistant message), the tool result comes
back (+1 tool message), and the loop repeats. A competent agent answers a
simple question in 1–2 requests. This one burned 18.

### 3. Turns get slower as the window fills

```text
[2026-09-17 08:26:15] Running chat completion on conversation with 39 messages.
[2026-09-17 08:26:15] Streaming response...
[2026-09-17 08:28:38] Prompt processing progress: 100.0%
```

The same prompt-processing phase that took ~1 s at message 7 now takes
**2 minutes 23 seconds** — the entire growing history is re-tokenized every
turn. The loop does not just waste requests; each request is more expensive
than the last.

### 4. Compaction: the context is silently rewritten mid-task

```text
[2026-09-17 08:28:40] Finished streaming response
[2026-09-17 08:28:47] Running chat completion on conversation with 17 messages.
```

39 messages in, **17 messages out**: VS Code hit the window limit and compacted
the conversation into a summary. The model loses the verbatim history — exactly
the details it would need to recover — and the loop starts over on top of the
summary:

```text
[2026-09-17 08:29:21] Running chat completion on conversation with 20 messages.
[2026-09-17 08:29:46] Client disconnected. Stopping generation...
```

The user cancelled. Total: ~9 minutes, ~20 requests, ~0 useful output.

## Root causes

1. **The model is too small for agentic tool calling.** At 1.5B parameters,
   Qwen2.5-Coder does not reliably make the meta-decision "I have enough
   information, stop calling tools, write the final answer." Every response is
   another tool call, so the harness keeps the loop alive. This matches the
   known constraint: sub-~3B models are not useful in Agent mode
   (see [../setup-lmstudio-vscode-quickstart.md](../setup-lmstudio-vscode-quickstart.md)).

2. **~10K tokens of fixed overhead shrink the working window.** With system
   instructions + tool schemas consuming a third of the 32K window, the
   conversation reaches the compaction threshold after only ~18 short
   round-trips. A bare chat would have had room for hundreds.

3. **No prefix caching amplifies every loop iteration.** Because LM Studio
   re-processes the full prefix per request, loop iteration *N* costs more than
   iteration *N-1* (27 s at the start, 2m23s near the end). The failure mode is
   not just stuck — it is stuck *and accelerating in cost*.

4. **Compaction destroys recovery information.** When the window fills, VS Code
   summarizes history (39 -> 17 messages). Whatever the model had "learned"
   via tool results is compressed away, so the loop restarts without ever
   converging — the exact "compact and start again, never deliver" behavior
   observed.

## How to avoid this

- **Do not use 1.5B models in Agent mode.** Setting `toolCalling: false` removes
  the tool payload, but in the current observed VS Code build it also removes
  the model from the picker, so it is not a usable Ask/Edit workaround. Use
  LM Studio Chat or another chat-first client for this model, or use a >= 7B
  tool-calling-capable model for VS Code Agent mode.
- **Cancel early.** The tell-tale sign is visible in the log pattern above:
  message count climbing by 2 every few seconds with no final answer. If you
  see it, stop the request instead of waiting for compaction.
- **Prefer compaction over silent overflow**, but treat a compaction event on a
  *simple question* as a failure signal, not a normal event.
- For simple questions, use a zero-overhead client (LM Studio's own Chat tab,
  or a CLI like `llm`/`aider`) — see the alternatives list in
  [../README.md](../README.md).

## Related

- [../README.md](../README.md) — where the
  fixed ~34% overhead comes from.
- [../vscode-context-requirements.md](../vscode-context-requirements.md) — context
  sizing rules for local models.
- [../issues/vscode-model-picker-tool-calling-findings.md](../issues/vscode-model-picker-tool-calling-findings.md) —
  why disabling tool calling does not reliably expose an Ask-only model.
