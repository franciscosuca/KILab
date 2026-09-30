# Frontier Quality on Local Hardware — `presi/copilot/`

A 12-slide, self-contained HTML/CSS/JS slide deck built to the specification in
[`prompt.md`](../../prompt.md) (the narrative and generation spec distilled from
`BLOGS/Local LLM.md`, v3 / v3.1). It matches the restrained editorial feel of
[`../kimik3/`](../kimik3/).

## Run

Open `index.html` directly in a browser — it works from `file://` with no server
and no network connection. No external libraries, fonts, CDNs, or remote images.

You can also serve the folder with any static file server:

```sh
cd presi/copilot
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Navigation

- Scroll / swipe, or Arrow Up / Down, Page Up / Down, Space / Shift+Space, Home, End.
- Deep links `#1` … `#12`, a top progress bar, a bottom-right slide counter, and a
  navigation hint that disappears after the first slide.
- `prefers-reduced-motion` is respected (instant jumps, no fade/slide transitions).

## Slides

1. Cover — *Frontier Quality on Local Hardware*
2. Why local? — offline, privacy, saving money
3. Is there still a gap? — `Qwen3.8-27B-MLX-4bit` vs `gpt-6-luna` (AA index figure)
4. Dense vs. sparse (MoE)
5. The two hardware numbers — RAM and bandwidth
6. RAM is the hard constraint — weights + KV cache (estimates table)
7. Bandwidth is the speed — garage/highway analogy (output-rate estimates)
8. The software stack — server + harness
9. Choose a server — MLX vs GGUF
10. The harness tax — VS Code vs Pi (arena.ai figure + link)
11. An honest take
12. Closing — "…stop paying for what you can run yourself."

## Missing source media

The two intended figures live in the author's local Obsidian vault and were **not
available** in this workspace, so the deck renders clearly-labelled placeholders
instead of fabricating or hot-linking media:

- `assets/aa-intelligence-index.png` — slide 3
  (source: `Pasted image 20260924092213 2.png`)
- `assets/arena-harness-tax.gif` — slide 10
  (source: `Kapture 2026-09-30 at 18.57.45.gif`)

Drop those files into `assets/` and swap the `.placeholder` block for an `<img>`
in `index.html` to finish the deck. See [`assets/README.md`](assets/README.md).

All model weights, KV-cache, and tokens-per-second figures are **provisional
estimates** as defined in `prompt.md`, and are labelled as such in the deck.
