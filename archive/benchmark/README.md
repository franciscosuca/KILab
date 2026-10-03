# LLM Benchmark Utility

A lightweight, zero-dependency Python script to benchmark performance (tokens/sec) of models running in LM Studio.

## Usage

Run the script directly with `python3`:

```bash
python3 benchllm.py --model <model-id> --message "your prompt"
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `--model` | **Required**. The exact model ID from LM Studio. | N/A |
| `--message` | **Required**. The prompt to test. | N/A |
| `--port` | The port LM Studio is running on. | `11440` |
| `--maxtoken` | Maximum generated tokens for the test. | `300` |
| `--reasoning` | Reasoning effort level (`none`, `low`, `medium`, `high`). Automatically routes to `/v1/responses`. | `None` |
| `--endpoint` | Target endpoint (`chat` or `responses`). | Auto (`responses` if `--reasoning` is provided, else `chat`) |

### Examples

**Standard benchmark (Chat Completions):**

```bash
python3 benchllm.py --model google/gemma-4-e4b --message "Write a binary search in Python" --port 11440
```

**Benchmark with reasoning disabled / configured (Responses API):**

```bash
# Without reasoning (effort: none)
python3 benchllm.py --model qwen/qwen3.5-9b --message "Write a binary search in Python" --reasoning none --port 11440

# With low/medium/high reasoning effort
python3 benchllm.py --model qwen/qwen3.5-9b --message "Write a binary search in Python" --reasoning high --port 11440
```

## Output

The script generates a table showing:

- **Completion tokens**: Total tokens generated.
- **Reasoning tokens**: Tokens spent on internal thinking/reasoning (when applicable).
- **Wall-clock time**: Time from request start to completion.
- **Tokens/sec**: Average generation speed.
- **Prompt tokens**: Size of your input message.
