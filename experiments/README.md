# Generation Experiments

Run the same prompt on different models and compare what they produce, side by side.

This folder holds three prompt-based experiments and one app:

- **Experiments** (`self-destruct-app`, `rate-limiter-fix`, `presentation-decks`): each has a ready-to-use prompt, any starter files, and a way to judge the results. You don't run a benchmark script. You paste the prompt into two or more models (in the same harness), then compare the outputs, speed, and cost.
- **App** (`blind-llm-arena`): a local presentation app that sends one prompt to several models at once and hides their names until the audience has voted.

## What's in each folder

| Folder | Type | What it does | What you compare |
|---|---|---|---|
| [`self-destruct-app`](self-destruct-app/README.md) | Experiment | Models build a single-file HTML/Tailwind "Self-Destruct" button demo from scratch. | Requirements met, accessibility, visual polish, speed, context use, cost. |
| [`rate-limiter-fix`](rate-limiter-fix/README.md) | Experiment | Models fix 3 bugs and add 1 missing feature in a small JavaScript rate limiter. | Tests passed (x/5), quality rubric, response time, credits used. |
| [`presentation-decks`](presentation-decks/README.md) | Experiment | Three models each build a full-screen slide deck from the same workshop notes, using one prompt. | Design, structure, and polish of the decks, plus context use and cost. |
| [`blind-llm-arena`](blind-llm-arena/README.md) | App | Sends one prompt to the selected models, shuffles anonymous result cards, and reveals identities after voting. | Audience votes on live, previewable outputs. |

Three folders hold extra material:

- `self-destruct-app/results/` contains one frontier-vs-local run: two generated pages, a context-usage screenshot, and a written comparison.
- `rate-limiter-fix/results/<MODEL_NAME>/` doesn't exist yet. You create it when you run the experiment, so each model's edited files stay separate.
- `presentation-decks/` holds the finished results of one run: `gemma4/`, `gpt6luna/`, and `kimik3/`, one deck per model, each with a context-usage screenshot. Its README has the prompt and the links to open each deck.

## How an experiment works

1. Pick an experiment from the table above and open its README.
2. Run the same prompt on each model you want to compare, one session per model.
3. Compare the results with the scorecard in that experiment. Each experiment keeps its generated outputs in a `results/` folder.

To run the app instead, see the [`blind-llm-arena` README](blind-llm-arena/README.md). It needs Node.js and `npm install`; the experiments need no setup beyond a harness (`rate-limiter-fix` also needs Node.js 18+).

## Which one should I try?

- **Visual or open-ended output:** start with `self-destruct-app`, or with `presentation-decks` for a larger design task. You judge the result by looking at it.
- **Objective pass/fail:** start with `rate-limiter-fix`. An automatic test suite scores each model.
- **Live comparison with an audience:** use `blind-llm-arena`. People vote before they know which model wrote what.

## Rules for fair comparisons

- Use the same prompt, harness, and thinking level for every model, so the only variable is the model.
- Give each model its own working copy or file name, so runs don't overwrite each other.
- A single run is a snapshot. Repeat it a few times before drawing conclusions.

## Related

- [`inspect-benchmark`](../benchmarks/inspect-benchmark/README.md): standard benchmarks such as HumanEval, run with Inspect AI.
