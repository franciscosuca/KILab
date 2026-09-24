# HumanEval Results (Local Models)

## Context window used

All models used an 8,192-token context window, except
`openai/sandepa_ai_coder_435m_small_moe`, which only allowed a 512-token
context window.

## Reasoning setting

Reasoning was deactivated for the evaluations to avoid deliberate reasoning
output. However, the logs still contain some traces of reasoning-like output,
so deactivation did not remove every such trace from the recorded runs.

## How to determine tok/s from `.eval` logs

Each `.eval` file is a ZIP archive containing a `header.json` and one JSON per
sample under `samples/`.

### 1. Per-call tok/s (true single-stream speed)

Each `samples/<Task>/<id>_epoch_<n>.json` contains:

- `output.usage.output_tokens` — tokens generated in that model call
- `output.time` — seconds taken by that call

```
tok/s = output.usage.output_tokens / output.time
```

This is the closest measure of raw single-request generation speed. It covers
the whole API call (prompt processing + decode), so it slightly understates
pure decode speed for long prompts with short completions.

### 2. Aggregate wall-clock tok/s (parallel throughput)

`header.json` contains:

- `stats.model_usage.<model>.output_tokens` — total output tokens for the run
- `stats.started_at` / `stats.completed_at` — wall-clock window of the run

```
tok/s = stats.model_usage.<model>.output_tokens
        / (completed_at - started_at in seconds)
```

Because Inspect runs samples concurrently (`max_connections`), this is inflated
relative to single-stream speed. It measures effective throughput of the whole
eval, not per-request speed.

> **Note:** `inspect view` does not show a precomputed tok/s metric. Per sample,
> the **Model** event shows output tokens and the sample header shows the call
> **Time** — divide manually, or use `inspect log dump <file.eval>` to export
> the JSON for scripting.

## Results table (completed runs only) (@thesis)

Legend: 🟢 ultra-small (<1B) · 🟡 super-small (1–2B) · 🟠 small (2–8B) — models
selected for debugging purposes. See
[categories.md](model-evals/categories.md) for the tier definitions.

| Date       | Model                                 | Eval ID                  | Hardware         | Samples | Accuracy | Output tokens | Per-call tok/s (avg) | Per-call tok/s (min–max) | Wall-clock tok/s |
|------------|---------------------------------------|--------------------------|------------------|--------:|---------:|--------------:|---------------------:|-------------------------:|-----------------:|
| 2026-09-16 | 🟠 **openai/google/gemma-4-e2b**    | `Z3aGC5xSRKZHWKETXBr5wD` | Apple M1 · 8 GB  |     164 |    78.0% |        26,401 |                  1.2 |                  0.1–9.0 |             13.6 |
| 2026-09-16 | openai/qwen2.5-coder-3b-instruct-mlx@8bit | `SxqrXmmGMhvppHyPSi9xn4` | Apple M1 · 8 GB  |     164 |    69.5% |        20,277 |                  1.0 |                  0.1–4.8 |              4.7 |
| 2026-09-15 | openai/mistralai/ministral-3-3b       | `VH3ynvkyMre3AdahUsrxJk` | Apple M1 · 8 GB  |     164 |    68.3% |        26,027 |                  1.2 |                 0.2–10.6 |             15.2 |
| 2026-09-16 | openai/qwen2.5-coder-3b-instruct-mlx@4bit | `Ur4D7zLVMAg8GrW4m6QGPt` | Apple M1 · 8 GB  |     164 |    60.4% |        23,431 |                  1.5 |                 0.1–10.0 |              6.3 |
| 2026-09-16 | 🟡 **openai/qwen2.5-coder-1.5b-instruct-mlx** | `aebm7vdUWV9y3CFjLg6nKh` | Apple M1 · 8 GB  |     164 |    54.9% |        16,680 |                  5.9 |                 0.8–17.5 |             27.8 |
| 2026-09-16 | 🟢 **openai/lfm2.5-vl-450m-heretic** | `n72n2Ay6opmjZtuaCnHz8M` | Apple M1 · 8 GB  |     164 |    21.3% |        23,355 |                 17.2 |                 4.5–47.7 |             22.7 |
| 2026-09-16 | openai/gemma-3-270m-it-mlx            | `Frsjj5Fusp3nJ7bsk9URgL` | Apple M1 · 8 GB  |     164 |    13.4% |        33,790 |                  5.5 |                 0.4–33.9 |             29.7 |
| 2026-09-15 | openai/gemma3-270m-leetcode           | `AgBjpyJCt9rov8UkUQXe9S` | Apple M1 · 8 GB  |     164 |    12.2% |        40,312 |                 11.8 |                 2.9–54.2 |            105.8 |

## Uncompleted runs

| Date       | Model                                 | Eval ID                  | Hardware         | Samples (of 164) | Accuracy | Output tokens | Per-call tok/s (avg) | Per-call tok/s (min–max) | Wall-clock tok/s |
|------------|---------------------------------------|--------------------------|------------------|-----------------:|---------:|--------------:|---------------------:|-------------------------:|-----------------:|
| 2026-09-15 | openai/google/gemma-4-e2b             | `JBc5UFaEhZw3fE38r4hYnB` | Apple M1 · 8 GB  |         **51/164** |       — |        30,906 |                  2.6 |                  0.3–9.7 |              1.6 |
| 2026-09-15 | openai/google/gemma-4-e2b             | `4U5qsfhAF45nwV7QZN3PKK` | Apple M1 · 8 GB  |         **17/164** |       — |         2,917 |                  9.6 |                 7.3–11.9 |              8.8 |
| 2026-09-15 | openai/google/gemma-4-e2b             | `ZoicdUCddeyNmLsFAPeZUj` | Apple M1 · 8 GB  |        **122/164** |       — |        43,630 |                  0.9 |                  0.1–9.0 |                — |
| 2026-09-16 | openai/qwen/qwen3-4b-thinking-2507    | `KsGbnk53rHdjUSCZRVi946` | Apple M1 · 8 GB  |         **18/164** |       — |         1,928 |                  6.0 |                  5.3–6.6 |              1.6 |
| 2026-09-16 | openai/sandepa_ai_coder_435m_small_moe | `mQ9HmuttvuZFwCCtVqXFz3` | Apple M1 · 8 GB  |        **164/164** |       — |        26,522 |                 83.3 |                5.9–126.6 |              3.5 |
| 2026-09-16 | openai/Qwen2.5-Coder-3B-Instruct-MLX-4bit | `CHHcPBgUrcznrYWrLW4aeZ` | Apple M1 · 8 GB  |          **4/164** |       — |             — |                    — |                        — |                — |
| 2026-09-16 | openai/sandepa_ai_coder_435m_small_moe | `cVeDQt9GiimufBzY3cFZu7` | Apple M1 · 8 GB  |        **164/164** |       — |        26,522 |                 83.3 |                5.9–126.6 |             60.7 |
| 2026-09-16 | openai/sandepa_ai_coder_435m_small_moe | `fnMSDreBQNvaNrDXApXMxf` | Apple M1 · 8 GB  |        **164/164** |       — |        26,995 |                 82.6 |                5.9–126.6 |             65.4 |
| 2026-09-16 | openai/sandepa_ai_coder_435m_small_moe | `YEaHCvoQWxbznzs5Qz3LUM` | Apple M1 · 8 GB  |        **164/164** |       — |        26,760 |                 83.8 |                5.9–126.6 |            245.5 |
| 2026-09-16 | openai/sandepa_ai_coder_435m_small_moe | `T4AqQkrdFSiiBeVi5BkHrH` | Apple M1 · 8 GB  |        **164/164** |       — |        26,760 |                 83.8 |                5.9–126.6 |              8.6 |
| 2026-09-16 | openai/qwen/qwen3-vl-4b               | `Dab5emkcWaCcnyTTwYCFzY` | Apple M1 · 8 GB  |        **164/164** |       — |        17,878 |                  0.7 |                  0.1–4.6 |              1.1 |
| 2026-09-16 | openai/qwen/qwen3-vl-4b               | `7nBuju5htchLAMZXh6moZn` | Apple M1 · 8 GB  |        **164/164** |       — |        19,165 |                  0.7 |                  0.1–6.7 |              0.7 |
| 2026-09-17 | openai/deepseek-r1-0528-qwen3-8b-mlx | `6d6AJFrnZsuKedLu7zFGoy` | Apple M1 · 8 GB  |          **0/164** |       — |             — |                    — |                        — |                — |

Notes:

- Wall-clock tok/s for `gemma3-270m-leetcode` is high because the run used
  higher effective parallelism; compare per-call tok/s for raw speed.
- Accuracy is HumanEval pass rate from the run header (`results.scores[0]`).
- Uncompleted runs have no final accuracy (`—`); stats are computed from the
  samples recorded before the run stopped. Most were cancelled manually
  (`Task cancelled by user (abort)`); `CHHcPBgUrcznrYWrLW4aeZ` and
  `YEaHCvoQWxbznzs5Qz3LUM` hit a `ModelGenerateError`.
- Runs marked 164/164 in the uncompleted table generated all samples but the
  run errored before final scoring, so no accuracy was recorded.
- `6d6AJFrnZsuKedLu7zFGoy` (deepseek-r1-0528-qwen3-8b-mlx) has no samples yet;
  the run started 2026-09-17 and had not produced output when this table was
  updated.
