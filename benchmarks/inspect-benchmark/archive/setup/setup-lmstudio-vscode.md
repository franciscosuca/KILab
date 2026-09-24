# Local LLM Dev Setup Guide (macOS)

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
3. Default port: `11440` (adjust if needed)
4. Verify it's running:

```bash
curl http://127.0.0.1:11440/v1/models
```

---

## 2. Frontend — VS Code

**Install**

```bash
brew install --cask visual-studio-code
```

**Connect to LM Studio**

1. Install the **GitHub Copilot** extension
2. Open `settings.json` (`Cmd+Shift+P` → *Open User Settings JSON*)
3. Add your local provider:

```json
"github.copilot.chat.models": [
  {
    "name": "LM Studio",
    "vendor": "customendpoint",
    "apiKey": "any",
    "apiType": "chat-completions",
    "models": [
      {
        "id": "<model-id-from-curl>",
        "name": "LM Studio (local)",
        "url": "http://127.0.0.1:11440/v1",
        "toolCalling": true,
        "vision": false,
        "maxInputTokens": 32000,
        "maxOutputTokens": 8000
      }
    ]
  }
]
```

> Get the exact `id` from `curl http://127.0.0.1:11440/v1/models`

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

**2. Read from LM Studio Logs** — After any prompt, the server logs in LM Studio show the generation speed in real-time.

**What to look for**

| Metric | Target |
|--------|--------|
| Tokens/sec | > 20 tok/s for comfortable use |
| Time to first token | < 3s |
| Output quality | Correct, runnable code without hallucinated APIs |

> Compare at least 2 models on the same prompt before committing to one.
