# LLM Model Benchmark (VS Code + Copilot)

A tiny, repeatable test scenario for comparing small LLM models (e.g. GPT-5.4 mini,
Kimi v2.7, etc.) inside VS Code Copilot Chat. Designed so each run takes a few
minutes and grading takes under a minute — no long docs or code reading required.

## What's being tested

`rate-limiter.js` is a token-bucket rate limiter with **3 intentional bugs** and
**1 missing feature** (all marked with `BUG`/`TODO` comments). `rate-limiter.test.js`
is a fixed, unmodifiable test suite (5 tests) that only passes once everything is
fixed correctly. This gives you an objective, automatic pass/fail signal, plus a
short subjective quality check.

## How to run the benchmark for one model

1. Restore the starter file (undo any previous model's edits):
   ```bash
   git checkout -- test/llm-benchmark/rate-limiter.js
   ```
   (If this is a fresh/untracked folder, keep a backup copy of the original
   `rate-limiter.js` and copy it back instead.)
2. In VS Code, open Copilot Chat, switch the model picker to the model under test.
3. Open `rate-limiter.js` and `rate-limiter.test.js` so they're in context (or
   attach them explicitly).
4. Paste the prompt from [`PROMPT.md`](./PROMPT.md) into the chat.
5. Let the model edit the file, then run:
   ```bash
   node --test test/llm-benchmark/rate-limiter.test.js
   ```
6. Record the result in [`SCORECARD.md`](./SCORECARD.md):
   - Tests passed (x/5) from the terminal output.
   - Credits/premium requests consumed (shown in the Copilot chat request cost
     or your usage dashboard).
   - Wall-clock response time (rough, from prompt sent to final answer).
   - Quality score using [`RUBRIC.md`](./RUBRIC.md) (takes ~1 minute).
   - Any notable comment (1 line).

Repeat steps 1–6 per model, then compare rows in `SCORECARD.md`.

## Requirements

- Node.js 18+ (for the built-in `node --test` runner — no npm install needed).

## Files

- `rate-limiter.js` — starter file with bugs/TODO for the model to fix.
- `rate-limiter.test.js` — fixed test suite, do not let the model edit this file.
- `PROMPT.md` — exact prompt text to paste per model.
- `RUBRIC.md` — 1-minute quality checklist.
- `SCORECARD.md` — results table template to fill in per model.
