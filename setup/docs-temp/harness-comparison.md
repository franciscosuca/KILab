# Agent Harness Prompt-Overhead Comparison

The agent harness you choose determines how much of a model's context window is
used before it can work on your request. A large system prompt, tool manifest,
MCP configuration, or workspace context can consume thousands of tokens before
your code or question is added.

This reference compares CLI-first and hybrid coding harnesses by their rough
prompt overhead, supported environments, BYOK options, and compatibility with
LM Studio. Use it to identify harnesses that may leave more context available
for your task—especially when working with local models and smaller context
windows.

These figures are directional estimates, not results from a single controlled
benchmark. Actual usage depends on the selected model, enabled tools and skills,
MCP servers, workspace files, adapter, and configuration. Measure the exact
setup you plan to run before treating any range as definitive.

## How to read the tables

- **Prompt overhead** is the approximate fixed prompt cost contributed by the
  harness's system instructions and tool-related metadata. It excludes your
  request, repository content, and conversation history.
- **CLI-only harnesses** do not provide a native VS Code workflow, so the VS
  Code column is marked `N/A`.
- **BYOK** indicates whether you can bring your own OpenRouter or GitHub
  Copilot credentials. The exact authentication path may require a proxy or a
  compatible provider endpoint.
- **LM Studio support** generally means that the harness can connect through
  an OpenAI-compatible base URL; it does not guarantee that every feature or
  model will work unchanged.

## CLI-only harnesses

| Tool / Agent | Environment / primary type | VS Code prompt overhead | Non-VS Code / CLI prompt overhead | BYOK (OpenRouter & Copilot) | LM Studio support |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pi** | Terminal / CLI agent | *N/A (CLI only)* | **~400–1,000 tokens** *(~491 avg.)* | **OpenRouter:** Yes<br>**Copilot:** No *(requires proxy)* | **Yes** *(via OpenAI base URL)* |
| **Hermes Agent** | Daemon / CLI / gateways | *N/A (CLI / gateway)* | **~1,500–3,500 tokens** | **OpenRouter:** Yes<br>**Copilot:** No | **Yes** *(via custom OpenAI base URL)* |
| **OpenClaw** | CLI / background agent | *N/A (CLI / framework)* | **~1,000–2,000 tokens** *(minimal)*<br>**~5,000–10,000+ tokens** *(full)* | **OpenRouter:** Yes<br>**Copilot:** No | **Yes** *(via OpenAI base URL)* |

## CLI and VS Code harnesses

| Tool / Agent | Environment / primary type | VS Code prompt overhead | Non-VS Code / CLI prompt overhead | BYOK (OpenRouter & Copilot) | LM Studio support |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Continue** | VS Code / IDE extension | **~1,500–2,500 tokens** | **~1,500–2,500 tokens** *(JetBrains / CLI)* | **OpenRouter:** Yes *(native)*<br>**Copilot:** Yes *(native Copilot token)* | **Yes** *(native LM Studio option)* |
| **GitHub Copilot** | VS Code / CLI agent | **~3,000–6,000+ tokens** *(Agent Mode)* | **~12,000–20,000+ tokens** *(Copilot CLI)* | **OpenRouter:** No<br>**Copilot:** Native *(GitHub subscription)* | **No** *(locked to GitHub's managed API)* |

## References

The references below document the prompt and context behavior behind the
estimates. Titles without a verified URL are intentionally left unlinked
rather than guessed.

- **Pi:** [Pi repository documentation on GitHub](https://github.com/badlogic/pi-mono)
  and [Respan's coding-agent comparison](https://www.respan.ai/market-map/best/coding-agents).
- **Continue:** [Continue configuration documentation](https://docs.continue.dev/customize/deep-dives/configuration)
  and Respan's *Continue vs. Pi* analysis.
- **Hermes Agent:** *Hermes Agent Token Overhead Guide* and *Giving Hermes an
  Efficient Soul* (Medium).
- **OpenClaw:** [OpenClaw system-prompt architecture documentation](https://docs.openclaw.ai/concepts/system-prompt)
  and [OpenClaw context documentation](https://docs.openclaw.ai/concepts/context).
- **GitHub Copilot:** [GitHub Copilot CLI token-overhead analysis (Issue #2627)](https://github.com/github/copilot-cli/issues/2627)
  and [GitHub Copilot CLI context-management documentation](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management).
