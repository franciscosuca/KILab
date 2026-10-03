# Local LLM Benchmarks with Inspect AI

Runs [Inspect AI](https://inspect.aisi.org.uk/) benchmarks against any model
served through an OpenAI-compatible API, and stores every run per machine so
results from different computers can be told apart.

## Requirements

- **macOS.** `run.sh` uses `sysctl` and `sw_vers` to detect the machine.
- **[uv](https://docs.astral.sh/uv/)** to manage Python and dependencies.
- **Docker**, installed and running. Code-execution benchmarks (such as
  HumanEval) run the generated code in a sandboxed Docker container.
- **An inference server** that exposes an OpenAI-compatible API, with the model
  you want to evaluate loaded. Setup guides per server:
  - [LM Studio](servers/lmstudio.md)

## Setup

```bash
cd benchmarks/model-evals
uv sync
cp .env.example .env
```

Edit `.env` so that Inspect AI sends its requests to your inference server.
The values depend on the server; see its setup guide.

```bash
OPENAI_BASE_URL="<SERVER_URL>/v1"
OPENAI_API_KEY="<API_KEY>"
```

Commands that call Inspect directly need `uv run --env-file .env` so these
variables are loaded. `run.sh` already does this.

## Layout

```
benchmarks/
  machines/<machine-id>.json          # chip, RAM and notes of each machine
  servers/<server>.md                 # inference server setup guides
  model-evals/                        # uv project and run.sh
  results/<task>/<machine-id>/        # .eval logs and generated results.md
  results/<task>/comparison.md        # generated, compares machines side by side
  results/generate_results.py         # builds the two files above from the logs
  results/how-to-compute-tok-s.md     # how speed is derived from the logs
```

## Running benchmarks and tagging runs

Accuracy depends mostly on the model, but speed depends on the machine. To keep
results from different machines apart, run every benchmark through
`model-evals/run.sh` instead of calling `inspect eval` directly:

```bash
cd benchmarks/model-evals
./run.sh <task> <YOUR_MODEL_ID> [extra inspect eval options]
```

`<YOUR_MODEL_ID>` is the model identifier shown by your inference server,
without the `openai/` prefix, which `run.sh` adds.

For each run, `run.sh`:

1. **Detects the machine** from its chip and RAM and builds a machine ID, for
   example `m2-16gb` or `m4-pro-48gb`. Set `MACHINE=<id>` to override it.
2. **Creates `machines/<machine-id>.json`** if it does not exist yet. Add notes
   to it by hand, such as the OS or runtime details.
3. **Writes the logs to `results/<task>/<machine-id>/`**, so each machine has
   its own folder.
4. **Tags the run.** Every `.eval` log gets the tag `machine:<machine-id>` and
   the metadata `machine`, `chip`, `ram_gb`, and `os`. They are stored in the
   log's `header.json` under `eval.tags` and `eval.metadata`, so a log keeps
   its machine information even if you move the file.

`run.sh` cannot detect the quantization, context length, reasoning setting, or
inference runtime.
Pass them as extra metadata so they are stored with the run:

```bash
./run.sh humaneval <YOUR_MODEL_ID> \
  --metadata runtime=<RUNTIME> \
  --metadata quant=<QUANTIZATION> \
  --metadata ctx=<CONTEXT_LENGTH> \
  --metadata reasoning=<on|off>
```

Any other `inspect eval` option can be added after the model ID, for example
`--limit 10` to run a few samples only.

## Generating results tables

After you have the logs you want, build the tables from them:

```bash
python3 results/generate_results.py                 # all tasks and machines
python3 results/generate_results.py --task humaneval --machine m1-8gb
```

It needs only Python 3 and writes two kinds of files; nothing in them is edited
by hand, so rerun it whenever logs are added:

- `results/<task>/<machine-id>/results.md`: an accuracy table, a speed table,
  and the runs that did not complete, with the model, quantization, context
  length, and runtime of each run.
- `results/<task>/comparison.md`: accuracy and per-call tok/s with one column
  per machine, so the same model can be compared across machines.

Quantization, context length, reasoning, and runtime are read from the run metadata passed
to `run.sh`. For logs recorded without it, add a
`results/<task>/<machine-id>/run-metadata.json` with `defaults` and per-model
values; the quantization is otherwise parsed from the model name, and unknown
values show as `—`. The script refuses to overwrite a `results.md` it did not
generate, unless `--force` is passed.

## Available benchmarks

| Task            | `run.sh` task name | Tests                                                           |
|-----------------|--------------------|-----------------------------------------------------------------|
| HumanEval       | `humaneval`        | Python code generation, function completion, syntax correctness |
| IFEval          | `ifeval`           | Multi-step instruction following: formatting and structure      |
| GSM8K           | `gsm8k`            | Step-by-step logic and math reasoning                           |
| MMLU (0-shot)   | `mmlu_0_shot`      | General knowledge across science, humanities, and technology    |

For example:

```bash
./run.sh gsm8k <YOUR_MODEL_ID>
```

## Disabling reasoning / thinking effort

To disable reasoning or thinking token generation for reasoning models, pass
`-M max_thinking_tokens=0` (or `-M reasoning_effort=none`):

```bash
./run.sh humaneval <YOUR_MODEL_ID> -M max_thinking_tokens=0 --metadata reasoning=off
```

## Resuming interrupted runs

If a run is interrupted or your machine restarts during evaluation, resume it
from the last completed sample using `eval-retry`:

```bash
uv run --env-file .env inspect eval-retry \
  ../results/<task>/<machine-id>/<YOUR_LOG_FILE_NAME>.eval
```

Alternatively, open `uv run inspect view`, navigate to the **Task** tab for the
unfinished evaluation, and click **Retry** in the upper-right corner.

## Visualizing and comparing results

Inspect AI stores all run histories locally. To compare models and inspect
failure logs for one machine, run:

```bash
uv run inspect view --log-dir ../results/<task>/<machine-id>
```

This opens an interactive dashboard in your web browser at
`http://localhost:7575`.

Available features include:

- **Model comparison:** Side-by-side accuracy scores and pass/fail metrics
  across all benchmark runs.
- **Sample inspection:** View exact prompt text, generated responses, and
  execution errors for individual samples.
- **Token metrics:** Monitor response latency and output token length per test
  case.

Inspect does not show tok/s directly; see
[results/how-to-compute-tok-s.md](results/how-to-compute-tok-s.md).
