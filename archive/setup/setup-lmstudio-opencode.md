# Local LLM Dev Setup Guide — LM Studio + OpenCode (macOS)

> Prerequisites: [Homebrew](https://brew.sh) installed.

---

## 1. Backend — LM Studio

**Install**

```bash
brew install --cask lm-studio
```

**Start the local server**

1. Open LM Studio → load a model
2. Go to **Developer** tab → click **Start Server**
3. Default port: `1234` (adjust if needed)
4. Verify it's running:

```bash
curl http://127.0.0.1:1234/v1/models
```

---

## 2. Frontend — OpenCode

**Install**

```bash
brew install opencode
```

**Connect to LM Studio**

1. Open or create `~/.config/opencode/config.json`
2. Add the LM Studio provider:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1"
      },
      "models": {
        "<model-id>": {
          "name": "<model-display-name>",
          "tools": true
        }
      }
    }
  }
}
```

> Get the exact `model-id` from:
>
> ```bash
> curl http://127.0.0.1:1234/v1/models
> ```

1. Launch OpenCode from your project directory:

```bash
opencode
```

1. Use `/models` inside OpenCode to switch to your LM Studio model

---

## 3. Models

### 3.1 Find the best model for programming

1. Go to [openrouter.ai/rankings](https://openrouter.ai/rankings) → filter by **Coding**
2. Pick a top-ranked model (e.g. `Qwen2.5-Coder`, `DeepSeek-Coder`)
3. Note the model family and parameter size

### 3.2 Find a local version

- Search the model name on [huggingface.co](https://huggingface.co) or directly in LM Studio's model browser
- Filter by `MLX` format (Apple Silicon) or `GGUF` (cross-platform)
- Prefer `mlx-community/` or `lmstudio-community/` repos — they're pre-quantized and tested

### 3.3 Pick the right quantization for your hardware

A 4BIT quantized model needs roughly **~1 GB per billion parameters**.

| Size | Params | RAM needed (4BIT) | When to use |
|------|--------|-------------------|-------------|
| **Micro** | < 3B | < 3 GB | Autocomplete, inline suggestions, low-latency tasks, edge devices |
| **Small** | 7B–9B | ~5–7 GB | Everyday coding assistant, chat, fast responses on limited RAM |
| **Medium** | 14B–35B | ~10–22 GB | Complex reasoning, refactoring, multi-file context, 16GB+ RAM |

> Rule: always try one size up from what you think you need — the quality gap between 7B and 14B is significant for coding tasks.

---

### 3.4 Benchmark your model

**1. Accurate CLI Benchmark** — Use the included Python utility for precise wall-clock timing and tokens/sec calculation.

```bash
# From the benchmark folder
python3 benchllm.py --model <model-id> --message "Write a binary search in Python"
```

> See [contributions/setup-fco/benchmark/README.md](../benchmark/README.md) for full details.

**2. LM Studio built-in bench**

1. Load a model → go to **My Models** → click **Bench**
2. Run the default prompt suite — note `tok/s` (tokens per second)

**What to look for**

| Metric | Target |
|--------|--------|
| Tokens/sec | > 20 tok/s for comfortable use |
| Time to first token | < 3s |
| Output quality | Correct, runnable code without hallucinated APIs |

> Compare at least 2 models on the same prompt before committing to one.
