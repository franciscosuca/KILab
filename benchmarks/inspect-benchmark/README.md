# Local LLM Evaluation Guide: Inspect AI + LM Studio

This guide walks through setting up an isolated model evaluation workflow on
macOS with `uv`, Inspect AI, and LM Studio.

## Prerequisites and Hardware Notes

For an M1 Mac with 8 GB of RAM:

- **Docker:** Docker Desktop must be installed and actively running. Code-execution benchmarks (such as HumanEval) execute generated code inside a sandboxed Docker container for security and isolation.
- System memory is shared with VRAM. Keep local models small to prevent swap
  memory slowdowns.
- **Recommended models:**
  - `Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF` for coding and logic.
  - `Qwen/Qwen2.5-3B-Instruct-GGUF` for general assistance and planning.
  - `meta-llama/Llama-3.2-3B-Instruct-GGUF` for general knowledge and QA.
- **Quantization:** Use `Q4_K_M` or `Q5_K_M` GGUF formats.

## Project Setup with uv

Create a dedicated directory to isolate dependencies and evaluation logs:

```bash
mkdir model-evals && cd model-evals
uv init
uv add inspect-ai inspect-evals openai
```

## Environment Configuration

Create a `.env` file in the root of the `model-evals` folder to route all
Inspect AI API calls to your local LM Studio server:

```bash
echo 'OPENAI_BASE_URL="http://localhost:1234/v1"' > .env
echo 'OPENAI_API_KEY="lm-studio"' >> .env
```

To ensure `uv` automatically loads these variables, pass `--env-file .env`
when running Inspect commands.

## LM Studio Configuration

1. Launch LM Studio.
2. Search for and download a lightweight model suitable for 8 GB of RAM, such
   as `Qwen2.5-Coder-1.5B-Instruct`.
3. Load the model into memory.
4. Open the Developer / Local Server tab in the left sidebar.
5. Verify the server settings:
   - Port: `1234`
   - Cross-Origin Resource Sharing (CORS): Enabled
6. Click **Start Server**.
7. Copy the exact model identifier displayed at the top of the server tab,
   such as `qwen2.5-coder-1.5b-instruct` or
   `sandepa_ai_coder_435m_small_moe`.

## Executing Benchmarks

Ensure Docker Desktop is open and running in the background before executing
benchmarks. Run the pre-written benchmarks with `uv run --env-file .env`.

### Python Coding and Debugging (HumanEval)

Tests code generation, function completion, and syntax correctness.

```bash
uv run --env-file .env inspect eval inspect_evals/humaneval \
  --model openai/<YOUR_MODEL_ID>
```

### Complex Instruction Following and Planning (IFEval)

Tests multi-step constraint adherence, including formatting rules, bullet
constraints, and structured output.

```bash
uv run --env-file .env inspect eval inspect_evals/ifeval \
  --model openai/<YOUR_MODEL_ID>
```

### Step-by-Step Logic and Math (GSM8K)

Tests multi-step reasoning capabilities.

```bash
uv run --env-file .env inspect eval inspect_evals/gsm8k \
  --model openai/<YOUR_MODEL_ID>
```

### General Knowledge and QA (MMLU)

Tests general domain knowledge across science, humanities, and technology.

```bash
uv run --env-file .env inspect eval inspect_evals/mmlu_0_shot \
  --model openai/<YOUR_MODEL_ID>
```

## Disabling Reasoning / Thinking Effort

To disable reasoning or thinking token generation for reasoning models, pass
`-M max_thinking_tokens=0` (or `-M reasoning_effort=none`):

```bash
uv run --env-file .env inspect eval inspect_evals/humaneval \
  --model openai/<YOUR_MODEL_ID> \
  -M max_thinking_tokens=0
```

Example command:

```bash
uv run --env-file .env inspect eval inspect_evals/humaneval \
  --model openai/sandepa_ai_coder_435m_small_moe
```

## Resuming Interrupted Runs

If a test process is interrupted or your machine restarts during evaluation,
resume execution from the last completed sample using `eval-retry`:

```bash
uv run --env-file .env inspect eval-retry logs/<YOUR_LOG_FILE_NAME>.eval
```

Alternatively, open `uv run inspect view`, navigate to the **Task** tab for
the unfinished evaluation, and click **Retry** in the upper-right corner.

## Visualizing and Comparing Results

Inspect AI stores all run histories locally. To compare models and inspect
failure logs, run:

```bash
uv run inspect view
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