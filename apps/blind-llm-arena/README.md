# Blind LLM Arena

A standalone presentation app for the two skipped hands-on parts of the KILab v3 talk: run one code challenge across models, collect an anonymous audience vote, then reveal the model identities. The reveal also makes it easy to discuss the results in the later “show the results” section.

## Run it

Open `index.html` in a modern browser. The app starts in mock mode, so the benchmark can be demonstrated without model accounts or API keys. Tailwind CSS is loaded from its CDN, so an internet connection is needed for the styled experience.

1. Click **Run Benchmark** and let each anonymous card finish.
2. Ask the audience which result they prefer; the cards are shuffled on every run.
3. Click **Reveal Identities** after the vote.
4. Use **Run Again** to reshuffle and repeat. Toggle **Mock responses** off to use configured live endpoints.

Generated HTML can be opened in each result's **Preview** tab. Previews are isolated in sandboxed iframes; response text is displayed as text in the app.

## Configure live models

Edit the `CONFIG` object near the start of the script in `index.html`:

- `mockMode`: defaults to `true`; switch it off in the UI for live calls.
- `models`: add/remove model entries. Give each a unique `id`, display `name`, `provider`, optional provider `mark`, `protocol`, `baseUrl`, `model`, and (where needed) `apiKey`.
- `protocol: "openai-compatible"` uses `POST <baseUrl>/chat/completions` and supports OpenAI, LM Studio, and compatible cloud API proxies.
- `protocol: "ollama"` uses Ollama's `POST <baseUrl>/api/chat` endpoint.
- `requestTimeoutMs` controls the per-model request timeout. Optional `headers` can supply proxy-specific headers.

The example OpenAI and proxy entries intentionally have empty keys, and the proxy URL is a placeholder. Configure every live target before switching off mock mode. Browser requests need CORS enabled on the API endpoint; Ollama users may need to configure its allowed origins. API keys placed in an HTML file are visible to anyone who can access that file. Keep the app local or use a private proxy; never publish real credentials in a client-side app.

Mock responses and delays are also in `CONFIG.models`. Set `mockError` on an entry to a message to demonstrate an individual provider failure while the other requests complete.
