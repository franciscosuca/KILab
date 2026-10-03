# Presentation Decks: One Prompt, Three Models

The same prompt was given to three models, each in its own [Pi](https://github.com/earendil-works/pi) session. Each model built a single-page slide deck from the same workshop notes. Open the three results and compare the design, structure, and polish.

You judge the result by looking at it, so no test suite is involved. The prompt below asks for open-ended design work, so the three decks differ a lot in slide count and layout.

## The prompt

```
based on the content from /Users/franciscosusana/workspace/vault/LEARNING/AISDLC - Workshop Preparation.md Build a single-page presentation website with full-screen slide sections and smooth keyboard/scroll snapping. Use a clean, human-designed aesthetic with neutral muted tones, high-contrast typography, generous whitespace, and subtle fade transitions. Avoid generic AI design tropes like floating neon shapes, purple glassmorphism, heavy gradients, or cluttered stock illustrations. Keep each slide focused on a single key point with minimal UI. Your results should be in a folder under /Users/franciscosusana/workspace/KILab/presi.
```

The source file (`AISDLC - Workshop Preparation.md`) is in a private notes vault and isn't part of this repo. It was reduced to its `v2` content just before the run. Re-running the prompt on today's version of the notes would give different slide content.

## Results

Open each `index.html` directly in a browser. No server or install is needed.

| Folder | Model | Provider | Open the deck | Context usage screenshot |
|---|---|---|---|---|
| [`gemma4/`](gemma4/) | `gemma-4-26B-A4B-it-QAT-MLX-4bit` (local) | oMLX | [`index.html`](gemma4/index.html) | [screenshot](gemma4/Screenshot%202026-09-30%20at%2017.55.26.png) |
| [`gpt6luna/`](gpt6luna/) | `gpt-6-luna` (frontier, `max` thinking) | GitHub Copilot | [`index.html`](gpt6luna/index.html) | [screenshot](gpt6luna/Screenshot%202026-09-30%20at%2017.54.55.png) |
| [`kimik3/`](kimik3/) | `kimi-k3` (`high` thinking) | GitHub Copilot | [`index.html`](kimik3/index.html) | [screenshot](kimik3/Screenshot%202026-09-30%20at%2017.54.24.png) |

`gpt6luna/` also has its own [`README.md`](gpt6luna/README.md), written by the model.

## Context use

From the Pi footer in each screenshot. The screenshots were taken later the same day (about 17:55 local time), before any further prompts were sent in those sessions.

| | gemma-4-26B | gpt-6-luna | kimi-k3 |
|---|---|---|---|
| Context used | 6.2k / 128k tokens (5%) | 42.1k / 1.0M tokens (4%) | 23.5k / 1.0M tokens (2%) |
| Cost | 0 credits (local) | 2.67 Copilot credits, $0.027 | $0.321 (subscription) |

The numbers are not like-for-like. The `kimi-k3` session switched over from `gpt-6-luna` and already held an earlier turn (a cleanup of the notes file), and the `gemma-4` session had a few chat turns before the prompt. Treat them as rough indications. Tokens per second and time to finish were not captured.

## How it was run

1. Three Pi sessions were opened at the same time with `/Users/franciscosusana/workspace/KILab` as the working directory, one per model.
2. The identical prompt was pasted into each session on 2026-09-30.
3. Each model wrote its files into `presi/`, since the prompt only said "a folder under `presi`":
   - `gemma4`: wrote `index.html`, `style.css`, `script.js`, then was asked to move the files into a folder named `gemma4`.
   - `gpt6luna`: wrote into `presi/local-ai-field-guide/`, later renamed to `gpt6luna/`.
   - `kimik3`: wrote `index.html`, `styles.css`, `script.js` directly into `presi/`, later moved into `kimik3/`.

The two later renames were done outside the sessions, so they aren't in the logs.

## Source sessions

Pi sessions in `~/.pi/agent/sessions/--Users-franciscosusana-workspace-KILab--/`:

- `2026-09-30T05-16-17-586Z_01a0f0bd-fb32-71eb-ade5-6d4fad5c11cb.jsonl` (`kimi-k3`)
- `2026-09-30T05-28-49-946Z_01a0f0c9-7619-7337-a93c-764d5ba25d28.jsonl` (`gpt-6-luna`)
- `2026-09-30T05-29-08-503Z_01a0f0c9-be97-7364-99d0-7faa05240cb6.jsonl` (`gemma-4`)

## Tips

- Use one prompt, one harness, and the same thinking level for every model, so the only variable is the model. This run did not match the thinking level across models (`max` for `gpt-6-luna`, `high` for `kimi-k3`).
- A single run is a snapshot. Repeat it a few times before drawing conclusions.
