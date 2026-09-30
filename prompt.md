# Prompt: Build the local-LLM presentation deck

Act as a senior front-end engineer and presentation designer. Implement the presentation described below as a polished, self-contained browser-based slide deck. Treat this file as the build specification and implement it in the repository; do not merely summarize the instructions.

## Goal and output

Create a 12-slide presentation titled **“Frontier Quality on Local Hardware”** for the AISDLC workshop. The deck should feel and behave like the editorial HTML deck in `presi/kimik3/`, while following the content and requirements below.

Write the result to **`presi/copilot/`**. Create:

- `presi/copilot/index.html`
- `presi/copilot/styles.css`
- `presi/copilot/script.js`
- `presi/copilot/assets/` for the two supplied local media files, if available

Do not overwrite or modify `presi/gemma4/`, `presi/gpt6luna/`, `presi/kimik3/`, `apps/`, or this prompt. Keep the deck usable when `index.html` is opened directly from disk (`file://`). Do not use external libraries, fonts, CDNs, remote images, or other network-dependent assets.

## Narrative and slide content

Use one main idea per slide, concise copy, and a clear spoken-through-line. Exclude the items marked `[skip]` in the source outline.

1. **Cover / introduction** — “Frontier Quality on Local Hardware”; AISDLC Workshop kicker; one-line promise about open-weight models, memory and bandwidth, inference servers, and harnesses. Include a restrained presenter line based only on the public profile at <https://github.com/franciscosuca>. Do not invent biographical details.
2. **Why local?** — offline access, privacy, and saving money. Briefly ground the talk in the speaker’s curiosity-driven exploration and early mistakes testing Ollama on an M1 in VS Code; keep the slide focused and concise.
3. **Is there still a gap?** — introduce the comparison between **Qwen3.8-27B-MLX-4bit** (local open-weight) and **gpt-6-luna** (frontier). Use the supplied Artificial Analysis Intelligence Index chart as the visual evidence. Its annotations distinguish closed models ($$$), open but large models ($$), and small/medium open-weight models ($). Do not imply that one chart proves universal equivalence; frame the comparison with appropriate nuance.
4. **Dense vs. sparse (MoE)** — explain that dense models use all parameters for each token, while MoE models activate selected experts. Clarify that all model weights still need to fit in memory. Mention LMFIT as a way to match models to hardware.
5. **The two hardware numbers** — RAM answers “can it fit?”; memory bandwidth helps answer “how fast can it generate?”.
6. **RAM is the hard constraint** — explain model-weight size plus KV-cache memory. Present the model requirements below clearly and legibly; do not shrink the type to force an overly wide table. Explain that the KV cache grows with context length and depends on architecture and cache precision.
7. **Bandwidth is the speed** — use the garage/highway analogy: RAM is whether the car fits in the garage; bandwidth is how quickly it travels. Connect GB/s to generated tokens/s and show the indicative output-rate estimates below.
8. **The software stack: server + harness** — the server runs the model; the harness supplies the prompt and presents the result.
9. **Choose a server** — MLX is optimized for Apple Silicon; GGUF is cross-platform. Recommend starting with defaults. Explain the performance trade-off behind the source outline’s recommendation to avoid Ollama, without making unsupported universal claims. Include a small `[benchmark link to come]` note rather than inventing benchmark results.
10. **The harness tax** — contrast heavier IDEs such as VS Code, which may add system/context overhead, with lighter clients such as Pi. Embed the supplied arena.ai cost-scaling GIF above a link to <https://arena.ai/blog/coding-agents-harness-tax>.
11. **An honest take** — frontier tools are easier and remain a strong choice. Local models can be sufficient for many everyday tasks, with privacy, cost, and availability trade-offs explained honestly.
12. **Closing** — end with the question: “The question isn’t whether local AI can compete. It’s whether you’re ready to stop paying for what you can run yourself.” Add “Thank you.”

## Model and hardware requirements

Use these names exactly:

- Local comparison model: `Qwen3.8-27B-MLX-4bit`
- Frontier comparison model: `gpt-6-luna`
- Additional hardware comparison models: `Gemma-4-26B-A4B-it-QAT-MLX-4bit` and `Qwen3.5-9B-MLX-4bit`

Use this provisional comparison data. Label the figures as **estimates**, not guaranteed model requirements or benchmark results:

| Model | Assumed architecture | Weights | KV cache @32K | KV cache @128K | KV cache @256K | Machine RAM @128K context |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.8-27B-MLX-4bit | Dense; assumed ~48 layers / 8 KV heads | ~14.5 GB | ~6 GB | ~24 GB | ~48 GB | 64 GB recommended; 48 GB tight |
| Gemma-4-26B-A4B-it-QAT-MLX-4bit | MoE; 26B total / 4B active; assumed hybrid attention | ~14 GB | ~3 GB | ~13 GB | ~26 GB | 48 GB |
| Qwen3.5-9B-MLX-4bit | Dense; assumed ~36 layers / 8 KV heads | ~5 GB | ~4.5 GB | ~18 GB | ~36 GB | 32 GB tight |

Calculation assumptions to show in a compact note or visual footnote:

- 4-bit weights are estimated as ~0.5 bytes per parameter plus ~7% overhead.
- KV-cache estimates assume FP16 cache and use `2 × layers × KV heads × head dimension × 2 bytes` per token. The layer/head assumptions above are estimates and must not be presented as verified model specifications.
- Budget roughly 8 GB for the OS and other apps in the machine-RAM estimate.
- 4-bit KV cache can reduce KV-cache memory (roughly one quarter of FP16, model/runtime dependent); do not mix this with the FP16 table values.
- The figures depend on the exact model architecture, runtime, context settings, and quantization. Do not invent greater precision or claim that these estimates are official. If repository material provides verified architecture details, prefer those and explain any resulting adjustment.

For generated-token speed, use the source specification’s rough bandwidth illustration:

- Approximate rule: `tokens/s ≈ memory bandwidth (GB/s) ÷ GB of weights read per generated token`.
- At an illustrative 200 GB/s: Qwen3.8-27B dense ~15 tok/s; Gemma-4 A4B MoE ~80 tok/s (assume ~2.5 GB read per token); Qwen3.5-9B dense ~44 tok/s.
- Treat these as idealized estimates; real results may be about 60–80% of the estimate and depend on hardware, runtime, context length, and implementation. For MoE, explain that active parameters affect per-token work, but avoid implying that only active weights need to fit in RAM.
- Prefill and token generation have different performance characteristics. Say input prefill is often faster than generation when appropriate; do not claim it is “always” faster without benchmark evidence.
- Teaching point: **weights decide whether it fits; KV cache constrains usable context; bandwidth influences how fast it talks.**

## Required media

The two intended source files are in the author’s local Obsidian vault (outside this repository):

1. `Pasted image 20260924092213 2.png` — Artificial Analysis Intelligence Index chart with handwritten market/size annotations. Use as the slide 3 figure.
2. `Kapture 2026-09-30 at 18.57.45.gif` — arena.ai SWE-bench Lite cost-scaling chart replay. Use on slide 10 above the harness-tax article link.

Use local copies in `presi/copilot/assets/` with clear stable filenames, for example `aa-intelligence-index.png` and `arena-harness-tax.gif`. If those files are not available in the workspace, do **not** fabricate, download, or substitute media. Keep a graceful, visibly identified figure placeholder with a useful caption, and report that the source assets need to be supplied. Never use a broken remote URL as a substitute.

## Visual design

Match the restrained editorial feel of `presi/kimik3/`:

- Warm paper background (`#f5f3ee`), dark ink (`#1e1b16`), muted body text, hairline rules, and a single muted-clay accent (`#9a4e22`) used sparingly.
- Serif display headings using a system-safe Iowan/Palatino/Georgia stack; system sans-serif body text; monospace styling for technical values and placeholders.
- Generous whitespace, short declarative copy, one key point per slide, and uppercase numbered kickers with a small accent dash.
- Use quiet key/value rows for comparisons. Style figures full-width where appropriate with a fine border and a small muted caption. Do not add decorative imagery beyond the two specified media files.
- Keep model names and technical claims readable. Avoid dense paragraphs and tiny text; split content into clear visual groups within the 12-slide limit.

## Interaction and implementation requirements

- Build a full-viewport slide deck with vertical CSS scroll-snap.
- Support Arrow Up/Down, Page Up/Down, Space/Shift+Space, Home, and End keyboard navigation; do not intercept keys while a link or form control is active.
- Support deep links `#1` through `#12`, a thin top progress bar, a bottom-right slide counter, and an initial navigation hint that disappears after the first slide.
- Reveal slide content with restrained staggered fade-up transitions. Respect `prefers-reduced-motion`.
- Make it responsive: on narrow screens, stack comparison rows and ensure every slide remains readable and reachable without clipped content.
- Use semantic HTML, meaningful image alt text, visible keyboard focus, sufficient contrast, and accessible labels for interactive controls.
- Keep HTML, CSS, and JavaScript local to the output folder. Do not add unnecessary dependencies.

## Acceptance checklist

Before finishing, verify:

- Exactly 12 slides are present, in the specified narrative order.
- The output is in `presi/copilot/` and existing decks and app files are unchanged.
- All model names, table values, caveats, and media behavior match this specification.
- The deck works from `file://` without a server or network connection (except that the article link opens externally when selected).
- Keyboard navigation, deep links, progress/counter updates, responsive layout, and reduced-motion behavior work.
- No model-specific RAM, KV-cache, or speed values are invented or presented as certain when they are estimates.
- Report the files created, any missing source media, and checks performed.
