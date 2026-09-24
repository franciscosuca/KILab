# IDE Benchmark Guide — VS Code & OpenCode

How to benchmark local LLMs when using them through VS Code (GitHub Copilot) or OpenCode as an AI coding assistant.

The CLI utility (`benchllm.py`) measures raw model throughput against a fixed prompt. This guide fills the gap: it defines representative coding tasks, explains how to capture **output quality**, **wall-clock time**, and **token counts** from inside each IDE, and provides a ready-made results table to compare models.

---

## 1. What to test

Use the five tasks below. They cover a spectrum from trivial to multi-step, so performance differences across models become visible.

| ID | Task | Prompt to send |
|----|------|----------------|
| T1 | Simple algorithm | `Write a binary search function in Python. Include a docstring and handle the empty-list case.` |
| T2 | Class design | `Create a Python ShoppingCart class with add_item, remove_item, and total methods. Use type hints.` |
| T3 | Bug fix | `The function below returns wrong results. Find and fix all bugs, and explain each fix.` + paste the buggy snippet |
| T4 | Refactor | `Refactor this synchronous Python code to use async/await. Keep the same logic and add error handling.` + paste the sync snippet |
| T5 | REST endpoint | `Write a FastAPI GET endpoint /products that returns a paginated list from a mock database. Include a unit test using pytest and httpx.` |

> Run every task against each model you want to compare. Keep the prompt text identical across runs.

---

## 2. Measuring in VS Code (GitHub Copilot + LM Studio)

### 2.1 Capture wall-clock time and token counts

LM Studio logs every request in real time. After each prompt:

1. Open LM Studio → **Developer** tab → scroll to the latest request entry.
2. Record:
   - **eval duration** — total generation time in seconds (wall-clock time)
   - **eval rate** — tokens/sec
   - **prompt_eval_count** — prompt tokens consumed
   - **eval_count** — completion tokens generated

Example log entry (truncated):

```text
POST /v1/chat/completions
...
"eval_count": 312,
"prompt_eval_count": 48,
"eval_duration": 12.4s,
"eval_rate": 25.2 tok/s
```

> If the entry is collapsed, click the row to expand it, or switch to the **Logs** view and search for `eval_count`.

### 2.2 Capture time manually (fallback)

If LM Studio logs are not visible, use your system clock:

1. Note the time just before you send the prompt in VS Code Chat.
2. Note the time when the last token appears in the response pane.
3. Subtract to get wall-clock time.

This method does **not** give you token counts — use it only when LM Studio logs are unavailable.

### 2.3 Evaluate output quality

After the model responds, score each task using the checklist in [Section 4](#4-quality-scoring-checklist).

---

## 3. Measuring in OpenCode

### 3.1 Capture wall-clock time and token counts

OpenCode displays token usage at the bottom of every response. After the assistant finishes:

1. Look at the status bar at the bottom of the OpenCode TUI — it shows:
   - **Tokens in / tokens out** for the last exchange
   - Cost estimate (shows `$0.00` for local models, which you can ignore)
2. For wall-clock time, OpenCode does not show it natively. Use one of these two methods:

**Method A — LM Studio logs (most accurate)**

Same as VS Code: read `eval_duration` and `eval_rate` from LM Studio's Developer tab after each prompt.

**Method B — Shell timer**

Open a second terminal and measure the time from when you press Enter to when the OpenCode cursor returns:

```bash
# In a separate terminal, watch LM Studio logs in real time
# (adjust port if yours differs from 1234)
curl -s http://127.0.0.1:1234/v1/models   # verify server is up
```

Then, inside OpenCode, note the wall-clock time from your system clock before and after sending the message, the same as in Section 2.2.

### 3.2 Read the session token total

To see cumulative token usage for the full OpenCode session:

- The token counter in the status bar updates after each exchange.
- For a per-task measurement, note the counter before and after each prompt and subtract.

### 3.3 Evaluate output quality

Score each response using the checklist in [Section 4](#4-quality-scoring-checklist).

---

## 4. Quality scoring checklist

Apply the same checklist to every model / every task for a fair comparison.

| Criterion | Score | Description |
|-----------|-------|-------------|
| **Runs without errors** | 0–2 | 0 = syntax/runtime errors, 1 = runs with warnings, 2 = clean execution |
| **Correct output** | 0–2 | 0 = wrong result, 1 = partially correct, 2 = fully correct |
| **Edge cases handled** | 0–1 | 0 = crashes or ignores edge cases, 1 = handles them explicitly |
| **Idiomatic style** | 0–1 | 0 = works but ignores language conventions, 1 = clean, idiomatic code |
| **Explains its work** | 0–1 | 0 = no explanation, 1 = brief inline comments or explanation provided |

**Maximum score per task: 7**

> Use a fixed test script or REPL to validate correctness. For T1–T4, copy the generated code into a Python REPL or file and run it. For T5, run `pytest` against the generated test file (requires `pip install pytest httpx` if not already available).

---

## 5. Results table template

Copy this table into your notes or `benchmarking-progress.md` and fill it in after each run.

### Task T1 — Binary search

| Model | Frontend | Backend | Wall-clock (s) | Tok/s | Prompt tok | Completion tok | Quality score (/7) | Notes |
|-------|----------|---------|---------------:|------:|-----------:|---------------:|-------------------:|-------|
| `model-id` | VS Code | LM Studio | — | — | — | — | — | |
| `model-id` | OpenCode | LM Studio | — | — | — | — | — | |

> Duplicate this section for T2–T5.

### Comparison summary

After completing all tasks, fill in the aggregate table:

| Model | Frontend | Avg wall-clock (s) | Avg tok/s | Total prompt tok | Total completion tok | Avg quality (/7) |
|-------|----------|--------------------|-----------|-----------------|---------------------|-----------------|
| `model-id` | VS Code | — | — | — | — | — |
| `model-id` | OpenCode | — | — | — | — | — |

---

## 6. Step-by-step workflow

Follow this sequence for a complete, reproducible benchmark run:

1. **Prepare the test prompts** — copy the five prompts from [Section 1](#1-what-to-test) into a text file so you can paste them consistently.
2. **Start your backend** — open LM Studio, load the model, start the server. Verify with `curl http://127.0.0.1:1234/v1/models` (should return a JSON list of loaded models).
3. **Open VS Code** — open a project folder, open the Copilot Chat panel (`Ctrl+Alt+I` / `Cmd+Alt+I`).
4. **Run T1–T5 in VS Code**:
   a. Paste the prompt → press Enter.
   b. Wait for the full response.
   c. Switch to LM Studio Developer tab → record `eval_duration`, `eval_rate`, `eval_count`, `prompt_eval_count`.
   d. Score the output using the checklist in [Section 4](#4-quality-scoring-checklist).
   e. Enter all values in the results table.
5. **Open OpenCode** — `cd` into the same project folder and run `opencode`.
6. **Run T1–T5 in OpenCode**:
   a. Paste the same prompt → press Enter.
   b. Wait for the full response.
   c. Read token counts from the OpenCode status bar; read timing from LM Studio logs.
   d. Score the output using the same checklist.
   e. Enter all values in the results table.
7. **Switch model** — reload a different model in LM Studio, repeat steps 4–6.
8. **Fill in the summary table** — compute averages and compare models side by side.

---

## 7. Tips for consistent results

- Always **clear the conversation context** between tasks (start a new chat in VS Code; use `/clear` in OpenCode) to avoid prior context influencing token counts and response quality.
- Use the **same project folder** for all runs so the context provided to the model is identical.
- Run each task **once per model** for a quick comparison, or **three times and average** for a more reliable measurement.
- If a model freezes or times out, record `—` and note the issue in the **Notes** column. Refer to [benchmarking-progress.md](benchmarking-progress.md) for known freeze causes and fixes.
- Keep `maxInputTokens` consistent across models in your VS Code settings (`settings.json`) and your OpenCode config (`~/.config/opencode/config.json`) so the context window does not skew token counts.
