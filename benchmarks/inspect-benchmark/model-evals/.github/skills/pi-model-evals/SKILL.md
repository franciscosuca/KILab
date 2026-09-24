---
name: pi:model-evals
description: Gather macOS hardware info (chip, RAM) and compute tok/s results from Inspect AI .eval logs in this folder, formatted for the results.md table. Use with Pi (pi.dev) coding agent.
---

# Model Evals Results Skill (Pi)

Use this skill when working in `contributions/setup-fco/model-evals/` to report
or update benchmark results in [results.md](../results.md).

## 1. Get processor and RAM of this Apple machine

Run these commands (macOS only):

```bash
# Chip / processor name (e.g. "Apple M2 Pro")
sysctl -n machdep.cpu.brand_string

# RAM in GB
echo "$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 )) GB"

# Optional extra detail: chip variant + core counts
system_profiler SPHardwareDataType | grep -E "Chip|Memory|Cores"
```

Record: processor (e.g. "Apple M2 Pro"), RAM (e.g. "32 GB").

## 2. Get results for the results.md table

`.eval` files in [logs/](logs/) are ZIP archives. Use this Python script to
extract one table row per **completed** run (skip files without `header.json`
or with `status != "success"`):

```python
import zipfile, json, glob
from datetime import datetime

for f in sorted(glob.glob("logs/*.eval")):
    z = zipfile.ZipFile(f)
    if "header.json" not in z.namelist():
        continue  # interrupted run
    h = json.loads(z.read("header.json"))
    if h.get("status") != "success":
        continue  # errored run
    ev, st = h["eval"], h["stats"]
    model = ev["model"]
    wall = (datetime.fromisoformat(st["completed_at"])
            - datetime.fromisoformat(st["started_at"])).total_seconds()
    u = st["model_usage"][model]
    rates, n = [], 0
    for name in z.namelist():
        if name.startswith("samples/") and name.endswith(".json"):
            s = json.loads(z.read(name))
            o = s.get("output") or {}
            if o.get("time") and o.get("usage"):
                n += 1
                if o["time"] > 0:
                    rates.append(o["usage"]["output_tokens"] / o["time"])
    acc = h["results"]["scores"][0]["metrics"]["accuracy"]["value"] * 100
    print(model, ev["eval_id"], n, f"{acc:.1f}%", u["output_tokens"],
          f"{sum(rates)/len(rates):.1f}",
          f"{min(rates):.1f}–{max(rates):.1f}",
          f"{u['output_tokens']/wall:.1f}")
```

Columns produced (in order), matching the results.md table:

| Column | Source |
|--------|--------|
| Model | `header.json → eval.model` |
| Eval ID | `header.json → eval.eval_id` |
| Samples | count of sample files with output usage |
| Accuracy | `header.json → results.scores[0].metrics.accuracy.value` × 100 |
| Output tokens | `header.json → stats.model_usage.<model>.output_tokens` |
| Per-call tok/s (avg) | mean of `output.usage.output_tokens / output.time` across samples |
| Per-call tok/s (min–max) | min and max of the same per-sample ratio |
| Wall-clock tok/s | total output tokens ÷ (`completed_at` − `started_at`) |

Date comes from the log filename prefix (`YYYY-MM-DDTHH-MM-SS`).

## Rules

- Only include runs with `status == "success"`; interrupted runs lack
  `header.json` and errored runs have `status == "error"`.
- Never invent values — if a field is missing, leave it out and say so.
- Do not edit `results.md` directly with this skill; that is the job of the
  `Model Evals Results Updater` agent, which invokes this skill.
