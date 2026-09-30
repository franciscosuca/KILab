# Blind LLM Arena

A local presentation app that sends one prompt to selected models, shuffles their anonymous result cards, and reveals model identities only after voting.

## Run it

Requirements:

- Node.js 18 or newer
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

Override local endpoints with `LMSTUDIO_BASE_URL`, `OMLX_BASE_URL`, or `OLLAMA_BASE_URL`. The UI can also register OpenAI-compatible and Ollama models manually. For safety, manual endpoints must resolve to `localhost`, `127.0.0.1`, or `::1`.

Select the models to include before each run. Their assignment to Model A, Model B, and subsequent cards is cryptographically shuffled and changes between runs when possible.

## Execution and artifacts

Local models are prompted through `curl`. Copilot models are prompted through the official SDK's authenticated Copilot CLI runtime, with tools denied. The server writes every completed response to a mode-`0600` file in a uniquely named operating-system temporary directory, reads that artifact for display, and deletes the directory after one hour.

Generated HTML can be opened in each result's **Preview** tab. Previews use sandboxed iframes, and response source is rendered as text.

## Validate

```bash
npm test
```
