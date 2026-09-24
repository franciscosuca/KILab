# Local LLM — CLI Benchmark Progress

**Hardware:** Apple M5 · 32 GB unified memory · macOS 26  
**Last updated:** June 26, 2026

> Raw throughput measurements using `benchllm.py`. No IDE frontend involved — results reflect pure backend performance.

---

## Installed Tools

| Tool | Type | Port | Status |
|------|------|------|--------|
| Ollama | Backend | `11434` | ✅ Installed |
| LM Studio | Backend + GUI | `11440` | ✅ Installed |
| oMLX | Backend | `8000` | ✅ Installed |
| benchllm.py | CLI Utility | — | ✅ Created |

---

## Benchmark Results

> **Prompt:** *"Analyze this entire repository, list all dependencies, and draft an end-to-end architecture diagram using Mermaid format."*  
> Run with `python3 benchllm.py --model <model-id> --message "<prompt>" --port <port>`.  
> For models supporting configurable reasoning (e.g. `qwen/qwen3.5-9b`), append `--reasoning none|low|medium|high` (targets `/v1/responses`).

### `qwen2.5-coder:7b`

| Backend | Reasoning | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Notes |
|---------|-----------|--------:|-----------:|-----------:|---------------:|-------|
| Ollama | N/A | — | — | — | — | |
| LM Studio | N/A | — | — | — | — | |
| oMLX | N/A | — | — | — | — | |

### `google/gemma-4-e4b`

| Backend | Reasoning | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Notes |
|---------|-----------|--------:|-----------:|-----------:|---------------:|-------|
| LM Studio | none | 25.4 | 11.78s | 22 | — | Synthetic (binary search) |
| oMLX | none | — | — | — | — | |

### `qwen/qwen3.5-9b`

| Backend | Reasoning | Tok/sec | Wall-clock | Prompt Tok | Completion Tok | Notes |
|---------|-----------|--------:|-----------:|-----------:|---------------:|-------|
| LM Studio | none | 24.7 | 12.09s | 16 | — | Synthetic (binary search), `/v1/responses` |
| LM Studio | low | — | — | — | — | |
| LM Studio | medium | — | — | — | — | |
| LM Studio | high | — | — | — | — | |

---

## Known Issues

| Issue | Model | Context | Suspected cause | Fix to try |
|-------|-------|---------|-----------------|------------|

---

## Open Questions

- [ ] Should `INSTRUCTIONS.md` always be used to reduce token consumption when prompting?
- [ ] Which repo to use for the structured evaluation run?
- [ ] Can CLI vs IDE agents performance gap be quantified?
