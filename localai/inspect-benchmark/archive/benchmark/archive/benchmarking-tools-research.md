# Benchmarking Tools for LM Studio

Comparison of tools that can measure **tokens/sec**, **time to first token**, and **output quality** against an LM Studio local server (OpenAI-compatible API on `http://127.0.0.1:1234/v1`).

---

## Comparison Table

| Tool | Install method | Uninstall | Measures tok/s | TTFT | Multi-model | macOS support | Notes |
|------|---------------|-----------|----------------|------|-------------|---------------|-------|
| **Manual benchmark script** | None (`python3` built-in) | N/A | ✅ (calculated) | ❌ | Manual | ✅ | Zero dependencies; table output |
| **`llm` CLI** (simonw) | `uv tool install llm` | `uv tool uninstall llm` | Via response timing | ❌ | One at a time | ✅ | General-purpose LLM CLI; logs to SQLite |
| **LM Studio built-in logs** | None (built-in) | N/A | ✅ (server logs) | ✅ | Current model only | ✅ | Read directly from Developer tab |
| **LM-Studio-Bench** (Ajimaru) | `git clone` + `setup.sh` | Delete folder + `~/.local/share/lm-studio-bench/` | ✅ | ✅ | ✅ (auto-discovers all) | ⚠️ Untested | Web dashboard; leaves SQLite cache, logs, results in `~/.local/share/` |
| **llmperf** (ray-project) | `git clone` + `pip install -e .` | Delete folder + venv | ✅ | ✅ | ✅ | ✅ | **Archived** (Dec 2025); requires Ray; heavy dependencies |

---

## Detailed Analysis

### 1. Manual benchmark script (Recommended)

**What it is:** A single `python3` command (no dependencies beyond the standard library) that times the request and outputs a results table.

```bash
python3 -c "
import json, time, urllib.request

url = 'http://127.0.0.1:1234/v1/chat/completions'
data = json.dumps({
    'model': '<model-id>',
    'messages': [{'role':'user','content':'Write a binary search in Python'}],
    'max_tokens': 300
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
start = time.time()
with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())
elapsed = time.time() - start

u = r['usage']
toks = u['completion_tokens']
tps = toks / elapsed if elapsed > 0 else 0

print()
print(f'| {\"Metric\":<20} | {\"Value\":<20} |')
print(f'|{\"-\"*22}|{\"-\"*22}|')
print(f'| {\"Model\":<20} | {r[\"model\"]:<20} |')
print(f'| {\"Completion tokens\":<20} | {toks:<20} |')
print(f'| {\"Wall-clock time\":<20} | {elapsed:.2f}s{\"\":<16} |')
print(f'| {\"Tokens/sec\":<20} | {tps:.1f}{\"\":<17} |')
print(f'| {\"Prompt tokens\":<20} | {u[\"prompt_tokens\"]:<20} |')
"
```

> Change `url` port and `model` to match your LM Studio setup. Get the model id from `curl http://127.0.0.1:1234/v1/models`.

| Advantage | Disadvantage |
|-----------|--------------|
| Zero install, zero cleanup | No streaming TTFT measurement |
| Works on any OS with curl | Manual calculation needed |
| No files left behind | No automated multi-model comparison |
| Fully transparent — you see exactly what runs | Tedious for many models |

---

### 2. LM Studio Built-in Logs

**What it is:** LM Studio's Developer tab shows tok/s and timing for every request in real time.

| Advantage | Disadvantage |
|-----------|--------------|
| Zero install | Only the currently loaded model |
| Shows tok/s, TTFT natively | No export/comparison across models |
| No cleanup needed | Must switch models manually |
| Accurate (measured server-side) | No scripting/automation |

---

### 3. `llm` CLI by Simon Willison

**What it is:** A well-maintained Python CLI tool (12k+ GitHub stars, 63 releases) that talks to any OpenAI-compatible endpoint. Not a dedicated benchmark tool, but can be scripted for timed comparisons.

```bash
# Install
uv tool install llm

# Point at LM Studio
llm aliases set lmstudio openai/chat:<model-id> --api-base http://127.0.0.1:1234/v1 --api-key any

# Time a prompt
time llm -m lmstudio "Write a binary search in Python"

# Uninstall (complete removal)
uv tool uninstall llm
```

| Advantage | Disadvantage |
|-----------|--------------|
| Proper PyPI package — clean `uv tool install/uninstall` | Not a dedicated benchmarker |
| Active maintenance (latest: Apr 2026) | No built-in tok/s calculation |
| Logs all responses to SQLite for later analysis | TTFT not directly measured |
| Plugin ecosystem, OpenAI-compatible out of the box | Requires scripting a loop for multi-model |
| Clean removal: `uv tool uninstall llm` removes everything | — |

---

### 4. LM-Studio-Bench (Ajimaru)

**What it is:** A feature-rich benchmark suite with web dashboard, auto-discovery of all installed models, progressive GPU offload testing, and PDF/CSV/HTML reports.

```bash
git clone https://github.com/Ajimaru/LM-Studio-Bench.git
cd LM-Studio-Bench
./setup.sh  # creates venv, installs deps
./run.py --all
```

| Advantage | Disadvantage |
|-----------|--------------|
| Auto-discovers all local models | **Not on PyPI** — no `pip install` / `uv tool install` |
| Measures tok/s, TTFT, VRAM | Leaves files in `~/.local/share/lm-studio-bench/` (logs, SQLite, results) |
| Web dashboard with charts | macOS listed as "untested" |
| Statistical evaluation (warmup + multiple runs) | Requires Python 3.10+ |
| PDF/CSV/HTML export | Heavy cleanup: delete repo + `~/.local/share/lm-studio-bench/` |

---

### 5. llmperf (ray-project)

**What it is:** A load-testing and correctness tool for LLM APIs, supporting OpenAI-compatible endpoints.

| Advantage | Disadvantage |
|-----------|--------------|
| Measures throughput and inter-token latency | **Archived** (Dec 2025) — no future updates |
| Supports concurrent request testing | Requires Ray (heavy dependency) |
| OpenAI-compatible endpoint support | Git-clone only — not on PyPI as a usable package |
| Statistical analysis with Jupyter notebook | Complex setup for a simple local benchmark |

---

## Recommendation

For your use case (macOS, simplicity, easy install/removal):

| Priority | Tool |
|----------|------|
| **1st — Quickest** | **LM Studio built-in logs** — just read tok/s from the Developer tab after each prompt |
| **2nd — Scriptable** | **Manual benchmark script** — zero install, outputs a table with tok/s automatically |
| **3rd — Richer tooling** | **`llm` CLI** — `uv tool install llm` / `uv tool uninstall llm`, logs to SQLite, easy to script |

Avoid LM-Studio-Bench and llmperf for your scenario — both require git clones, scatter files across your system, and are harder to fully remove.
