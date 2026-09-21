# Prompt to paste per model

Paste this exact text into Copilot Chat with `rate-limiter.js` and
`rate-limiter.test.js` open/attached:

```
Open rate-limiter.js. It's a token-bucket rate limiter with 3 known bugs and
1 missing feature, each marked with a BUG or TODO comment. Fix the bugs and
implement the missing feature so every test in rate-limiter.test.js passes.

Constraints:
- Do not change the public API: class name `RateLimiter`, method signatures
  `tryRequest(key)` and `reset(key)`.
- Do not edit rate-limiter.test.js.
- No external dependencies.
- Keep the file under ~60 lines.

After editing, reply with a 2-3 sentence summary of what you changed and why.
```

Keep the prompt identical across models so results are comparable.
