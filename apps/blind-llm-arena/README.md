# Blind LLM Arena

A local presentation app that sends one prompt to selected models, shuffles their anonymous result cards, and reveals model identities only after voting.

## Run it

Requirements:

- Node.js 20.19 or newer (22.12+ for Node 22)
- `curl`
- Any local providers you want to use
- GitHub Copilot CLI installed and authenticated if you want Copilot models

```bash
cd apps/blind-llm-arena
npm install
npm start
```

Open <http://127.0.0.1:4173>. The app starts in mock mode. Turn **Mock responses** off to make live requests.

## Model discovery and registration

At startup and whenever **Refresh models** is selected, the server checks:

- LM Studio at `http://127.0.0.1:1234/v1`
- oMLX at `http://127.0.0.1:8000/v1`
- Ollama at `http://127.0.0.1:11434`
- the authenticated Copilot CLI through the official `@github/copilot-sdk`

Override local endpoints with `LMSTUDIO_BASE_URL`, `OMLX_BASE_URL`, or `OLLAMA_BASE_URL`. The UI can also register OpenAI-compatible and Ollama models manually. For safety, manual endpoints must use `localhost`, `127.0.0.1`, or `::1`.

For authenticated APIs, credentials are selected in this order:

1. The API key entered when registering a model.
2. `OMLX_API_KEY`, `LMSTUDIO_API_KEY`, or `OLLAMA_API_KEY` for the matching endpoint and protocol.
3. For OpenAI-compatible endpoints, the matching provider's key in pi's `~/.pi/agent/models.json` (or `$PI_CODING_AGENT_DIR/models.json`). The normalized Base URL must match exactly; credentials are never reused for a different host, port, or path. Pi literal keys and `$VAR` / `${VAR}` references are supported; `!command` values are not executed.

Leaving the manual API-key field blank inherits these server-side credentials rather than disabling authentication. Keys are not returned to the browser or put in process arguments. HTTP 401/403 errors explain how to configure a key.

Nothing is selected by default — check the models to include before each run. Copilot's Auto entries are omitted. Assignment to Model A, Model B, and subsequent cards is cryptographically shuffled and changes between runs when possible.

## Execution and artifacts

Local models are prompted through their API (`curl` for unauthenticated requests and the built-in HTTP client when a bearer key is needed). Copilot models are prompted through the official SDK's authenticated Copilot CLI runtime, with tools denied. The server writes every completed response to a mode-`0600` file in a uniquely named operating-system temporary directory, reads that artifact for display, and deletes the directory after one hour.

Generated HTML can be opened in each result's **Preview** tab. Previews use sandboxed iframes, and response source is rendered as text.

## Validate

```bash
npm test
```
