# Self-Destruct App: Same Prompt, Any Models

A quick, repeatable test: give one prompt to two or more models in the **same harness**, then open the generated pages side by side and compare the output, speed, context use, and cost. It works with any mix of frontier and local models.

The models build a single-file HTML/Tailwind "Self-Destruct" button demo: a confirmation, a 10-second countdown, a cancel option, a destruction animation, and a reset. You judge the result by looking at it, so no test suite is involved.

## What you need

- **A harness** that can switch models and write files, such as [Pi](https://github.com/earendil-works/pi), GitHub Copilot, or Claude Code. Pi is a light terminal harness, so it adds little system prompt and tool overhead. Setup is in the [coding-agent-pack README](../../../coding-agent-pack/README.md).
- **Two or more models** to compare. A frontier model needs a subscription or API key. A local model needs an OpenAI-compatible server, such as [oMLX](https://github.com/jundot/omlx), [LM Studio](https://lmstudio.ai), or [Ollama](https://ollama.com).
- **A web browser** to open the generated HTML files.

## Run the test

1. Open one terminal or chat session per model, each with this folder as the working directory:

   ```bash
   cd benchmarks/generation-experiments/self-destruct-app/results
   ```

2. In each session, select a different model. In Pi, for example:

   ```bash
   pi --model <provider>/<model-id>
   ```

   In other harnesses, use the model picker.
3. Paste the prompt from [`PROMPT.md`](./PROMPT.md) into each session, replacing `<MODEL_NAME>` with a short name for that model. Keep the prompt identical across models.
4. Wait for each run to finish. Each model saves its own `self-destruct-<MODEL_NAME>.html` in `results/`, so parallel runs don't overwrite each other.
5. Open the generated files in a browser, side by side.
6. Record what you see in [`SCORECARD.md`](./SCORECARD.md). Note the time to finish, and the context and token use if your harness shows them.

## Files

- [`PROMPT.md`](./PROMPT.md): the exact prompt to paste.
- [`SCORECARD.md`](./SCORECARD.md): comparison table to fill in per model.
- [`results/`](results/README.md): generated pages and findings from a previous run. Your own outputs land here too.

## Tips

- Use one prompt, one harness, and the same thinking level for every model, so the only variable is the model.
- A single run is a snapshot. Repeat it a few times before drawing conclusions.
- In Pi, the measurement extensions show context usage and tokens per second:

  ```bash
  pi install npm:pi-context-usage
  pi install npm:pi-token-speed
  ```

- Local speed depends on your machine's RAM and memory bandwidth. A local model that fits in RAM can still be slow.
