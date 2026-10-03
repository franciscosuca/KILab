# Benchmark Categories (Speed & Accuracy)

Classification scheme for models benchmarked with [Inspect AI](https://inspect.aisi.org.uk/)
on HumanEval. These are practical community-informed tiers, not an industry
standard — Inspect itself reports raw metrics and defines no speed/accuracy
categories.

## Speed categories (single-stream per-call tok/s)

Use **per-call tok/s** (single request decode), not wall-clock tok/s, which is
inflated by parallelism. Prompt processing (TTFT) is excluded — tok/s here is
`output_tokens / call time`.

| Category                 | Range     | Meaning                                              |
|--------------------------|----------:|------------------------------------------------------|
| Too slow                 | <4 tok/s  | Output stalls conversational work; below reading pace |
| Barely acceptable        | 4–8       | Around human reading speed (~5 tok/s); tolerable     |
| Comfortable interactive  | 8–20      | Smooth enough for ordinary chat and iteration        |
| Fast                     | 20–40     | Responsive streaming; fine for coding assistance     |
| Very fast / real-time    | >40       | Generation is rarely the bottleneck                  |

Rationale: average silent reading is ~238 WPM ≈ 5.3 tok/s (0.75 words/token),
so anything under ~4 tok/s feels slower than reading. LocalLLaMA discussions
repeatedly frame ~5 tok/s as slow and 10–20+ as comfortable. There is no
verified "coding needs 30+ tok/s" rule; 20+ is defensibly fast.

## Accuracy categories (HumanEval pass@1, original split)

| Category      | Range   | Meaning for local/small coding models      |
|---------------|--------:|--------------------------------------------|
| Poor          | <20%    | Limited utility beyond simple completions  |
| Weak          | 20–39%  | Early / general small-model baseline       |
| Decent        | 40–59%  | Useful with tests, review, and retries     |
| Good          | 60–74%  | Strong local coding capability             |
| Excellent     | 75–84%  | Leading small/open local-model performance |
| Frontier-like | ≥85%    | Exceptional; check methodology carefully   |

Orientation points from the [EvalPlus leaderboard](https://evalplus.github.io/leaderboard.html)
(greedy decoding, original HumanEval): StarCoder 34.1%, CodeLlama-7B 37.8%,
DeepSeek-Coder-1.3B-Instruct 65.9%, Qwen2.5-Coder-32B-Instruct 92.1%.

> Compare like-for-like: don't mix original HumanEval with HumanEval+, or
> greedy with sampled decoding, in one comparison.

## Size classes (local inference context)

| Class      | Parameters | Examples            |
|------------|-----------:|---------------------|
| Tiny       | <1B        | 0.27B–0.5B models   |
| Small      | 1B–8B      | 1.5B, 3B, 4B, 7B    |
| Medium     | >8B–20B    | 13B/14B class       |
| Large      | >20B–70B   | 32B/34B/70B         |

"Small" has no universal boundary; a recent SLM survey uses <8B as its working
definition. Models under 1B are treated separately (tiny) since their speed
profile differs so much.

## Sources

- Inspect AI framework: https://inspect.aisi.org.uk/
- EvalPlus leaderboard: https://evalplus.github.io/leaderboard.html
- Original HumanEval (Codex) paper: https://arxiv.org/abs/2107.03374
- Qwen2.5-Coder technical report: https://arxiv.org/abs/2409.12186
- StarCoder results: https://huggingface.co/bigcode/starcoder
- SLM size-definition survey: https://arxiv.org/html/2501.05465v1
- LocalLLaMA acceptable tok/s: https://www.reddit.com/r/LocalLLaMA/comments/162pgx9/what_do_yall_consider_acceptable_tokens_per/
- LocalLLaMA minimum tok/s: https://www.reddit.com/r/LocalLLaMA/comments/1cuqye0/what_is_the_minimum_tokens_a_second_before_a/
