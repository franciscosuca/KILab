# Understanding Local LLMs: Inference Engines, Frontends & Models

Running LLMs locally means two things running simultaneously: a **backend** (inference engine) that loads the model and serves an API, and a **frontend** that connects to it and provides a UI or coding interface.

---

## 1. Backends — Inference Engines

The backend loads model weights into memory, handles hardware acceleration, and exposes a local OpenAI-compatible API. It has no UI of its own.

### Key options

| Engine | Platform | Format | Best for |
|--------|----------|--------|----------|
| **llama.cpp** | Windows · Linux · macOS | GGUF | Cross-platform, consumer GPUs |
| **oMLX** | macOS (Apple Silicon) | MLX | M-series chips, unified memory |
| **Ollama** | All | GGUF | Simplest local setup, single-user |
| **LM Studio** | All | GGUF + MLX | GUI + built-in server, beginner-friendly |
| **vLLM** | Linux + NVIDIA | Multiple | Multi-user production serving |
| **ExLlamaV2** | Windows · Linux | EXL2 | Consumer NVIDIA GPUs, aggressive quantization |

### GGUF vs MLX

| | GGUF | MLX |
|-|------|-----|
| Runtime | llama.cpp | Apple MLX framework |
| Platform | Cross-platform | Apple Silicon only |
| On Mac M-series | Works | Faster — native unified memory |

---

## 2. Frontends

Frontends connect to a running backend via API. They cannot generate text on their own.

| Type | Examples | Use case |
|------|----------|----------|
| **TUI / CLI** | OpenCode, Ollama CLI | Low overhead, agentic dev tasks |
| **IDE extension** | GitHub Copilot, Continue, Cline | In-editor coding assistance |
| **Desktop GUI** | LM Studio, Open WebUI | Chat, model management, parameter tuning |

> For coding tasks, a TUI agent (e.g. OpenCode) connected directly to a backend has lower latency than a GUI wrapper, because it manages context more efficiently.

---

## 3. Model Formats & Quantization

Quantization reduces model weight precision to shrink file size and RAM usage.  
Rule of thumb at **4BIT**: ~1 GB per billion parameters.

| Size class | Params | RAM (4BIT) | When to use |
|------------|--------|------------|-------------|
| **Micro** | < 3B | < 3 GB | Autocomplete, inline hints, edge devices |
| **Small** | 7B–9B | ~5–7 GB | Everyday coding assistant, fast responses |
| **Medium** | 14B–35B | ~10–22 GB | Complex reasoning, refactoring, long context |

### Common quantization levels (GGUF)

| Level | Quality | Size vs full |
|-------|---------|--------------|
| Q3_K_L | Low | ~25% |
| Q4_K_M | Good balance | ~33% |
| Q6_K | High | ~50% |
| Q8_0 | Near-lossless | ~66% |

For Apple Silicon, prefer **MLX 4BIT** over GGUF equivalents — same quality, faster due to unified memory.

---

## 4. How to Pick a Model for Local Development

1. Check [openrouter.ai/rankings](https://openrouter.ai/rankings) → filter by **Coding**
2. Note the top model family (e.g. `Qwen2.5-Coder`, `DeepSeek-Coder`)
3. Search for it on [huggingface.co](https://huggingface.co) or in LM Studio's browser
4. Pick an `mlx-community/` (Mac) or `lmstudio-community/` (cross-platform) quantized version
5. Verify it fits your RAM — then benchmark before committing

---

## 5. Further Reading

- [OpenCode CLI intro (YouTube)](https://youtu.be/MQxqc14s2gs?si=DXForHuuE0b9isHU)
- [Replace Claude Code with OpenCode + Local LLM? (YouTube)](https://youtu.be/8f5qWdx9L-Q?si=kIWyk350ssL7ZPsY)
