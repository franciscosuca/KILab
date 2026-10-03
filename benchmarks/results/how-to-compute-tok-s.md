# How to determine tok/s from `.eval` logs

Each `.eval` file is a ZIP archive containing a `header.json` and one JSON per
sample under `samples/`.

## 1. Per-call tok/s (true single-stream speed)

Each `samples/<Task>/<id>_epoch_<n>.json` contains:

- `output.usage.output_tokens` — tokens generated in that model call
- `output.time` — seconds taken by that call

```
tok/s = output.usage.output_tokens / output.time
```

This is the closest measure of raw single-request generation speed. It covers
the whole API call (prompt processing + decode), so it slightly understates
pure decode speed for long prompts with short completions.

## 2. Aggregate wall-clock tok/s (parallel throughput)

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
