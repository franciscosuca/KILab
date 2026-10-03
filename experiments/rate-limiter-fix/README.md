# Rate Limiter Fix: Same Prompt, Same Starter Files

A quick, repeatable test: give the same prompt and the same starter files to several models, then compare the results side by side. Each run takes a few minutes and grading takes about a minute.

You don't build anything here. The starter files and the prompt are already prepared, so you only run the prompt and judge what each model produces.

## What the models are asked to do

`rate-limiter.js` is a token-bucket rate limiter with **3 intentional bugs** and **1 missing feature**, all marked with `BUG`/`TODO` comments. `rate-limiter.test.js` is a fixed test suite (5 tests) that only passes once everything is fixed correctly. That gives you an automatic pass/fail signal plus a short subjective quality check.

## What you need

- **A harness** that can switch models and edit files, such as VS Code with GitHub Copilot Chat, [Pi](https://github.com/earendil-works/pi), or Claude Code.
- **Two or more models** to compare, for example a frontier model and a local one.
- Node.js 18+ for the built-in `node --test` runner. No `npm install` needed.

## Run the test

1. Give each model its own copy of the starter files, so runs can't affect each other:

   ```bash
   cd benchmarks/generation-experiments/rate-limiter-fix
   mkdir -p results/<MODEL_NAME>
   cp rate-limiter.js rate-limiter.test.js results/<MODEL_NAME>/
   ```

   Use a short model name such as `gpt-5.4-mini` or `qwen3.8-27b`. Each model's edited files stay in `results/<MODEL_NAME>/`, so you can compare them later.
2. Open `results/<MODEL_NAME>/` in your harness and select the model under test.
3. Paste the prompt from [`PROMPT.md`](./PROMPT.md), with both files open or attached. Keep the prompt identical across models.
4. When the model finishes, run its tests:

   ```bash
   node --test results/<MODEL_NAME>/rate-limiter.test.js
   ```
5. Record the result in [`SCORECARD.md`](./SCORECARD.md):
   - Tests passed (x/5) from the terminal output.
   - Credits or premium requests used (shown in the chat request cost or your usage dashboard).
   - Wall-clock response time, roughly from prompt sent to final answer.
   - Quality score from [`RUBRIC.md`](./RUBRIC.md).
   - Any notable comment, in one line.

Repeat for each model, then compare the rows in `SCORECARD.md`.

## Files

- [`rate-limiter.js`](./rate-limiter.js): starter file with the bugs and the TODO. Never edit it; copy it per run.
- [`rate-limiter.test.js`](./rate-limiter.test.js): fixed test suite. The model must not edit it.
- [`PROMPT.md`](./PROMPT.md): the exact prompt to paste.
- [`RUBRIC.md`](./RUBRIC.md): 1-minute quality checklist.
- [`SCORECARD.md`](./SCORECARD.md): results table to fill in per model.

## Tips

- Use one prompt, one harness, and the same thinking level for every model, so the only variable is the model.
- A single run is a snapshot. Repeat it a few times before drawing conclusions.
