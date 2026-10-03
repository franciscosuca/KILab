# Quality Rubric (~1 minute to score)

For each model run, check yes/no. Score = number of "yes" out of 5.

1. **Tests pass** — `node --test rate-limiter.test.js` shows 5/5 passing.
2. **API preserved** — `RateLimiter` class name and `tryRequest(key)` /
   `reset(key)` signatures unchanged.
3. **Scope respected** — no unrelated files edited, no extra dependencies
   added, `rate-limiter.test.js` untouched.
4. **Concise explanation** — final chat reply is ~2-3 sentences, accurate to
   the actual diff (no hallucinated changes).
5. **Minimal/clean diff** — fix stays close to ~60 lines, no dead code,
   no unnecessary refactor of unrelated parts.

Quality score = (yes count) / 5.
