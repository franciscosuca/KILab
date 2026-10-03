const DEMO_MODELS = [
  { id: "demo-a", name: "GPT-4o", provider: "OpenAI", mark: "O" },
  { id: "demo-b", name: "Qwen 2.5 72B", provider: "Ollama", mark: "Q" },
  { id: "demo-c", name: "Claude 3.5 Sonnet", provider: "Cloud API proxy", mark: "C" },
];

const MOCK_RESULTS = [
  "<!doctype html><html><body style=\"display:grid;place-items:center;min-height:100vh;background:#020617;color:white;font-family:sans-serif\"><button style=\"padding:18px 28px;border:0;border-radius:12px;background:#e11d48;color:white;font-weight:800\">ARM SELF-DESTRUCT</button></body></html>",
  "<!doctype html><html><body style=\"display:grid;place-items:center;min-height:100vh;background:#090909;color:white;font-family:sans-serif\"><button style=\"padding:22px 34px;border:1px solid #fca5a5;border-radius:99px;background:#dc2626;color:white;font-weight:800\">HOLD TO ARM</button></body></html>",
  "Mock model response. Switch off Mock responses to run the selected model.",
];

const state = {
  mockMode: true,
  running: false,
  hasRun: false,
  revealed: false,
  models: [...DEMO_MODELS],
  selectedIds: new Set(),
  assignments: [],
  previousSignature: "",
  cards: new Map(),
};

const $ = (selector) => document.querySelector(selector);
const elements = {
  prompt: $("#prompt-input"), grid: $("#result-grid"), run: $("#run-button"), runLabel: $("#run-label"),
  reveal: $("#reveal-button"), revealLabel: $("#reveal-label"), mode: $("#mode-toggle"),
  modeIndicator: $("#mode-indicator"), modeDescription: $("#mode-description"), summary: $("#run-summary"),
  revealBanner: $("#reveal-banner"), modelPicker: $("#model-picker"), modelCount: $("#model-count"),
  discoveryStatus: $("#discovery-status"), refreshModels: $("#refresh-models"), modelForm: $("#model-form"),
  modelFormStatus: $("#model-form-status"),
};

function isAutoModel(model) {
  const values = [model?.name, model?.id, model?.model];
  return values.some((value) => {
    const text = String(value || "").trim().toLowerCase();
    return text === "auto" || text.split(/[:/]/).pop() === "auto";
  });
}

function selectableModels(models) {
  return models.filter((model) => !isAutoModel(model));
}

function activeModels() {
  return state.models.filter(({ id }) => state.selectedIds.has(id));
}

function retainSelection(models) {
  const available = new Set(models.map(({ id }) => id));
  state.selectedIds = new Set([...state.selectedIds].filter((id) => available.has(id)));
}

function renderModelPicker() {
  elements.modelPicker.replaceChildren();
  for (const model of state.models) {
    const label = document.createElement("label");
    label.className = "model-choice";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = state.selectedIds.has(model.id);
    input.disabled = state.running;
    input.addEventListener("change", () => {
      if (input.checked) state.selectedIds.add(model.id);
      else state.selectedIds.delete(model.id);
      setupCards();
      renderModelPicker();
    });
    const copy = document.createElement("span");
    const name = document.createElement("strong");
    name.textContent = model.name || model.model;
    const provider = document.createElement("small");
    provider.textContent = model.provider;
    copy.append(name, provider);
    label.append(input, copy);
    elements.modelPicker.append(label);
  }
  elements.modelCount.textContent = `${activeModels().length} selected`;
}

function makeCard(letter) {
  const article = document.createElement("article");
  article.className = "result-card";
  article.innerHTML = `
    <div class="card-head"><div class="card-name"><span class="letter">${letter}</span><div><h2>Model ${letter}</h2><div class="identity" hidden></div></div></div><div class="status"><b>Ready</b><span>—</span></div></div>
    <div class="card-tabs"><div><button class="tab" data-view="response" aria-selected="true">Response</button><button class="tab" data-view="preview" aria-selected="false" hidden>Preview</button></div><button class="copy" hidden>Copy</button></div>
    <div class="card-body"><div class="empty">Run the benchmark<br>to see this response</div><pre class="response" hidden></pre><div class="error" hidden></div><div class="preview-status" role="status" aria-live="polite" hidden></div><iframe class="preview" title="Sandboxed HTML output preview" sandbox="allow-scripts" referrerpolicy="no-referrer" hidden></iframe></div>`;
  const card = {
    article, identity: article.querySelector(".identity"), status: article.querySelector(".status b"),
    latency: article.querySelector(".status span"), empty: article.querySelector(".empty"),
    response: article.querySelector(".response"), error: article.querySelector(".error"),
    preview: article.querySelector(".preview"), responseTab: article.querySelector('[data-view="response"]'),
    previewTab: article.querySelector('[data-view="preview"]'), copy: article.querySelector(".copy"),
    previewStatus: article.querySelector(".preview-status"),
    content: "", html: "", previewToken: "", previewStarted: false, previewReady: false,
    previewError: "", previewMessage: "", previewTimer: null,
  };
  article.addEventListener("click", async (event) => {
    const tab = event.target.closest("[data-view]");
    if (tab) showView(card, tab.dataset.view);
    if (event.target.closest(".copy")) {
      await navigator.clipboard.writeText(card.content);
      card.copy.textContent = "Copied";
      setTimeout(() => { card.copy.textContent = "Copy"; }, 1200);
    }
  });
  return card;
}

function setupCards() {
  state.hasRun = false;
  state.revealed = false;
  state.assignments = [];
  elements.reveal.disabled = true;
  elements.revealLabel.textContent = "Reveal Identities";
  elements.reveal.setAttribute("aria-pressed", "false");
  elements.revealBanner.hidden = true;
  for (const card of state.cards.values()) clearTimeout(card.previewTimer);
  elements.grid.replaceChildren();
  state.cards.clear();
  activeModels().forEach((_, index) => {
    const letter = String.fromCharCode(65 + index);
    const card = makeCard(letter);
    state.cards.set(letter, card);
    elements.grid.append(card.article);
  });
}

function shuffle(models) {
  const result = [...models];
  for (let index = result.length - 1; index > 0; index--) {
    const random = new Uint32Array(1);
    crypto.getRandomValues(random);
    const other = Math.floor((random[0] / 4294967296) * (index + 1));
    [result[index], result[other]] = [result[other], result[index]];
  }
  const signature = result.map(({ id }) => id).join("|");
  if (result.length > 1 && signature === state.previousSignature) result.push(result.shift());
  state.previousSignature = result.map(({ id }) => id).join("|");
  return result;
}

function htmlDocument(text, token) {
  const fenced = text.match(/```(?:html)?\s*\n([\s\S]*?)```/i)?.[1]?.trim();
  const value = fenced || text.trim();
  if (!/<!doctype\s+html|<html[\s>]/i.test(value)) return "";
  const documentNode = new DOMParser().parseFromString(value, "text/html");
  const policy = documentNode.createElement("meta");
  policy.httpEquiv = "Content-Security-Policy";
  policy.content = "default-src 'none'; script-src 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com/lucide@latest https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; form-action 'none'";
  const bridge = documentNode.createElement("script");
  bridge.textContent = `(() => {
    const token = ${JSON.stringify(token)};
    const send = (type, message = "") => parent.postMessage({ type, token, message }, "*");
    addEventListener("DOMContentLoaded", () => {
      send("arena-preview-ready");
      const reportSize = () => send("arena-preview-resize", String(Math.max(
        document.documentElement.scrollHeight, document.body?.scrollHeight || 0
      )));
      reportSize();
      const observer = new ResizeObserver(reportSize);
      observer.observe(document.documentElement);
      if (document.body) observer.observe(document.body);
    }, { once: true });
    addEventListener("error", (event) => {
      const message = event.target?.src
        ? "Could not load " + event.target.src
        : event.message || "The generated preview encountered a JavaScript error.";
      send("arena-preview-error", message);
    }, true);
    addEventListener("unhandledrejection", (event) => {
      send("arena-preview-error", event.reason?.message || String(event.reason));
    });
  })();`;
  documentNode.head.prepend(policy, bridge);
  return `<!doctype html>${documentNode.documentElement.outerHTML}`;
}

function renderPreviewStatus(card) {
  card.previewStatus.hidden = card.preview.hidden || (card.previewReady && !card.previewError);
  card.previewStatus.classList.toggle("error", Boolean(card.previewError));
  card.previewStatus.textContent = card.previewError
    ? `Preview issue: ${card.previewError}`
    : card.previewMessage;
}

function resetPreview(card) {
  clearTimeout(card.previewTimer);
  card.preview.removeAttribute("srcdoc");
  card.preview.style.height = "";
  card.previewToken = "";
  card.previewStarted = false;
  card.previewReady = false;
  card.previewError = "";
  card.previewMessage = "";
  card.previewStatus.hidden = true;
}

function showView(card, view) {
  const preview = view === "preview";
  if (preview && !card.html) return;
  card.response.hidden = preview;
  card.preview.hidden = !preview;
  card.responseTab.setAttribute("aria-selected", String(!preview));
  card.previewTab.setAttribute("aria-selected", String(preview));
  if (preview && !card.previewStarted) {
    card.previewStarted = true;
    card.previewMessage = "Loading interactive preview…";
    card.preview.srcdoc = card.html;
    card.previewTimer = setTimeout(() => {
      card.previewMessage = "Preview is still loading. Check your connection to the allowed CDNs.";
      renderPreviewStatus(card);
    }, 10000);
  }
  renderPreviewStatus(card);
}

window.addEventListener("message", (event) => {
  const data = event.data;
  if (!data || !["arena-preview-ready", "arena-preview-error", "arena-preview-resize"].includes(data.type)) return;
  for (const card of state.cards.values()) {
    // Sandboxed documents have an opaque origin; match the frame and per-response token instead.
    if (event.source !== card.preview.contentWindow || data.token !== card.previewToken) continue;
    if (data.type === "arena-preview-resize") {
      const height = Number(data.message);
      if (!card.preview.hidden && Number.isFinite(height) && height > 0) {
        card.preview.style.height = `${Math.min(900, Math.max(380, Math.ceil(height)))}px`;
      }
      break;
    }
    clearTimeout(card.previewTimer);
    if (data.type === "arena-preview-ready") card.previewReady = true;
    else if (!card.previewError) {
      card.previewError = typeof data.message === "string"
        ? data.message.slice(0, 500)
        : "The generated preview encountered a JavaScript error.";
    }
    renderPreviewStatus(card);
    break;
  }
});

function resetCard(card) {
  resetPreview(card);
  card.content = "";
  card.html = "";
  card.response.textContent = "";
  card.responseTab.setAttribute("aria-selected", "true");
  card.previewTab.setAttribute("aria-selected", "false");
  card.identity.hidden = true;
  card.identity.classList.remove("revealed");
  card.empty.hidden = false;
  card.response.hidden = true;
  card.error.hidden = true;
  card.preview.hidden = true;
  card.previewTab.hidden = true;
  card.copy.hidden = true;
  card.status.textContent = "Thinking";
  card.latency.textContent = "In progress";
}

function showResponse(card, text) {
  resetPreview(card);
  card.content = text;
  card.previewToken = crypto.randomUUID();
  card.html = htmlDocument(text, card.previewToken);
  card.empty.hidden = true;
  card.error.hidden = true;
  card.response.textContent = text;
  card.previewTab.hidden = !card.html;
  card.copy.hidden = false;
  showView(card, "response");
}

async function discoverModels() {
  elements.refreshModels.disabled = true;
  elements.discoveryStatus.textContent = "Checking local runtimes and Copilot…";
  try {
    const response = await fetch("/api/models");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    const models = selectableModels(payload.models);
    if (payload.models.length) {
      state.models = models;
      retainSelection(models);
      setupCards();
      renderModelPicker();
    }
    const up = payload.providers.filter(({ available }) => available).map(({ provider }) => provider);
    const down = payload.providers.filter(({ available }) => !available)
      .map(({ provider, error }) => `${provider}${error ? ` (${error})` : ""}`);
    elements.discoveryStatus.textContent = up.length
      ? `${models.length} models found · ${up.join(", ")}${down.length ? ` · unavailable: ${down.join("; ")}` : ""}`
      : `No runtimes found${down.length ? ` · ${down.join("; ")}` : ""}. Start a provider or register a loopback endpoint below.`;
  } catch (error) {
    elements.discoveryStatus.textContent = `Discovery unavailable (${error.message}). Mock models remain available.`;
  } finally {
    elements.refreshModels.disabled = false;
  }
}

async function requestModel(model, prompt, index) {
  if (state.mockMode) {
    await new Promise((resolve) => setTimeout(resolve, 650 + index * 250));
    return MOCK_RESULTS[index % MOCK_RESULTS.length];
  }
  const response = await fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ modelId: model.id, prompt }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload.text;
}

async function runBenchmark() {
  if (state.running) return;
  const prompt = elements.prompt.value.trim();
  const models = activeModels();
  if (!prompt) return elements.prompt.focus();
  if (!models.length) {
    elements.summary.textContent = "Select at least one model.";
    return;
  }
  state.running = true;
  state.hasRun = false;
  state.revealed = false;
  elements.revealBanner.hidden = true;
  elements.reveal.disabled = true;
  elements.run.disabled = true;
  elements.runLabel.textContent = "Running models…";
  renderModelPicker();
  state.assignments = shuffle(models).map((model, index) => ({ model, letter: [...state.cards.keys()][index] }));
  state.assignments.forEach(({ letter }) => resetCard(state.cards.get(letter)));
  let complete = 0;
  const started = performance.now();
  await Promise.allSettled(state.assignments.map(async ({ model, letter }, index) => {
    const card = state.cards.get(letter);
    const requestStarted = performance.now();
    try {
      showResponse(card, await requestModel(model, prompt, index));
      card.status.textContent = "Ready";
    } catch (error) {
      card.empty.hidden = true;
      card.error.hidden = false;
      card.error.textContent = error.message || "Unknown request error";
      card.status.textContent = "Error";
    } finally {
      card.latency.textContent = `${((performance.now() - requestStarted) / 1000).toFixed(2)} s`;
      elements.summary.textContent = `${++complete} / ${models.length} responses complete`;
    }
  }));
  const errors = state.assignments.filter(({ letter }) => state.cards.get(letter).status.textContent === "Error").length;
  state.running = false;
  state.hasRun = true;
  elements.run.disabled = false;
  elements.runLabel.textContent = "Run Again";
  elements.reveal.disabled = false;
  elements.summary.textContent = `${models.length - errors} ready${errors ? ` · ${errors} error${errors === 1 ? "" : "s"}` : ""} · ${((performance.now() - started) / 1000).toFixed(2)} s total`;
  renderModelPicker();
}

function revealIdentities(show) {
  state.revealed = show;
  elements.revealLabel.textContent = show ? "Hide Identities" : "Reveal Identities";
  elements.reveal.setAttribute("aria-pressed", String(show));
  elements.revealBanner.hidden = !show;
  state.assignments.forEach(({ model, letter }) => {
    const identity = state.cards.get(letter).identity;
    identity.textContent = `${model.provider} · ${model.name || model.model}`;
    identity.hidden = !show;
    identity.classList.toggle("revealed", show);
  });
}

function updateMode() {
  elements.mode.setAttribute("aria-checked", String(state.mockMode));
  elements.modeIndicator.textContent = state.mockMode ? "DEMO MODE" : "LIVE MODE";
  elements.modeDescription.textContent = state.mockMode ? "Safe demo · no model calls" : "Live requests · local server";
}

elements.mode.addEventListener("click", () => {
  if (!state.running) {
    state.mockMode = !state.mockMode;
    updateMode();
  }
});
elements.run.addEventListener("click", runBenchmark);
elements.reveal.addEventListener("click", () => state.hasRun && revealIdentities(!state.revealed));
elements.refreshModels.addEventListener("click", discoverModels);
elements.modelForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.modelFormStatus.textContent = "Registering…";
  try {
    const response = await fetch("/api/models", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(new FormData(elements.modelForm))),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    state.models = [...state.models.filter(({ id }) => id !== payload.model.id), payload.model];
    state.selectedIds.add(payload.model.id);
    setupCards();
    renderModelPicker();
    elements.modelFormStatus.textContent = `${payload.model.name} registered and selected.`;
  } catch (error) {
    elements.modelFormStatus.textContent = error.message;
  }
});

setupCards();
renderModelPicker();
updateMode();
discoverModels();
