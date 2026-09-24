# Local LLM — OpenCode Benchmark Progress

**Hardware:** Apple M5 · 32 GB unified memory · macOS 26  
**Last updated:** June 26, 2026

> IDE-based measurements using OpenCode (TUI). Results include output quality scores alongside throughput. See [benchmark-ide-guide.md](benchmark-ide-guide.md) for the full measurement procedure.

---

## Installed Tools

| Tool | Type | Port | Status |
|------|------|------|--------|
| Ollama | Backend | `11434` | ✅ Installed |
| LM Studio | Backend + GUI | `11440` | ✅ Installed |
| oMLX | Backend | `8000` | ✅ Installed |
| OpenCode | Frontend (TUI) | — | ✅ Installed |

---

## Benchmark Results

> **Prompt:** *"Analyze this entire repository, list all dependencies, and draft an end-to-end architecture diagram using Mermaid format."*  
> Read token counts from the OpenCode status bar; read timing from LM Studio Developer tab. Score output using the checklist in [benchmark-ide-guide.md § 4](benchmark-ide-guide.md#4-quality-scoring-checklist).

### `qwen2.5-coder:7b`

| Backend | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Quality (/7) | Notes |
|---------|--------:|-----------:|-----------:|---------------:|-------------:|-------|
| Ollama | — | — | — | — | — | |
| LM Studio | — | — | — | — | — | |
| oMLX | — | — | — | — | — | |

### `google/gemma-4-e4b`

| Backend | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Quality (/7) | Notes |
|---------|--------:|-----------:|-----------:|---------------:|-------------:|-------|
| LM Studio | — | — | — | — | — | Confirmed working |
| oMLX | — | — | — | — | — | |

### `qwen/qwen3.5-9b`

| Backend | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Quality (/7) | Notes |
|---------|--------:|-----------:|-----------:|---------------:|-------------:|-------|
| LM Studio | — | — | — | — | — | |

---

## Known Issues

| Issue | Model | Context | Suspected cause | Fix to try |
|-------|-------|---------|-----------------|------------|
| Freeze / no response | Qwen2.5 14B | OpenCode + LM Studio | `maxInputTokens: 128000` exhausts KV cache | Reduce to `16000–32000` |

---

## Open Questions

- [ ] Should `INSTRUCTIONS.md` always be used to reduce token consumption when prompting?
- [ ] Which repo to use for the structured evaluation run?
- [ ] Best generic BE + OpenCode combo to recommend to colleagues?
- [ ] Can CLI vs IDE agents performance gap be quantified?
