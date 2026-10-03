# Inference server: LM Studio

Setup of [LM Studio](https://lmstudio.ai/) as the OpenAI-compatible inference
server for the benchmarks in this folder. For everything else, see the
[benchmarks README](../README.md).

## Start the server

1. Launch LM Studio.
2. Download the model you want to evaluate.
3. Load the model into memory. Set the context length and quantization you
   want to evaluate at this point; both are fixed while the model is loaded.
4. Open the **Developer / Local Server** tab in the left sidebar.
5. Verify the server settings:
   - Port: `1234`
   - Cross-Origin Resource Sharing (CORS): Enabled
6. Click **Start Server**.
7. Copy the exact model identifier displayed at the top of the server tab.
   This is the `<YOUR_MODEL_ID>` used in the README commands.

## Point the benchmarks at LM Studio

In `benchmarks/model-evals/.env`:

```bash
OPENAI_BASE_URL="http://localhost:1234/v1"
OPENAI_API_KEY="lm-studio"
```

LM Studio does not check the API key, but the OpenAI client requires a value.

## Run

Pass the model identifier without the `openai/` prefix, because `run.sh` adds
it. Record the settings you chose in LM Studio as metadata, since `run.sh`
cannot detect them:

```bash
cd benchmarks/model-evals
./run.sh humaneval <YOUR_MODEL_ID> \
  --metadata runtime=lmstudio \
  --metadata quant=<QUANTIZATION> \
  --metadata ctx=<CONTEXT_LENGTH> \
  --metadata reasoning=<on|off>
```
