import { createServer } from "node:http";
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { homedir, tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CopilotClient } from "@github/copilot-sdk";

const APP_DIR = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 4173);
const REQUEST_TIMEOUT_MS = Number(process.env.MODEL_TIMEOUT_MS || 120000);
const DISCOVERY_TIMEOUT_MS = Number(process.env.DISCOVERY_TIMEOUT_MS || 5000);
const MAX_BODY_BYTES = 1024 * 1024;
const MAX_OUTPUT_BYTES = 10 * 1024 * 1024;

const registry = new Map();
const manualRegistry = new Map();
const artifacts = new Map();

const localProviders = [
  {
    provider: "LM Studio",
    protocol: "openai-compatible",
    mark: "L",
    baseUrl: process.env.LMSTUDIO_BASE_URL || "http://127.0.0.1:1234/v1",
    apiKey: process.env.LMSTUDIO_API_KEY || "",
  },
  {
    provider: "oMLX",
    protocol: "openai-compatible",
    mark: "M",
    baseUrl: process.env.OMLX_BASE_URL || "http://127.0.0.1:8000/v1",
    apiKey: process.env.OMLX_API_KEY || "",
  },
  {
    provider: "Ollama",
    protocol: "ollama",
    mark: "O",
    baseUrl: process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434",
    apiKey: process.env.OLLAMA_API_KEY || "",
  },
];

export function runCommand(command, args, { cwd, input, timeoutMs = REQUEST_TIMEOUT_MS } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, stdio: ["pipe", "pipe", "pipe"], env: process.env });
    const stdout = [];
    const stderr = [];
    let outputBytes = 0;
    let settled = false;

    const finish = (error, result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (error) reject(error);
      else resolve(result);
    };
    const collect = (chunks) => (chunk) => {
      outputBytes += chunk.length;
      if (outputBytes > MAX_OUTPUT_BYTES) {
        child.kill("SIGKILL");
        finish(new Error(`${command} produced too much output`));
        return;
      }
      chunks.push(chunk);
    };

    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.on("error", (error) => finish(new Error(`Could not start ${command}: ${error.message}`)));
    child.on("close", (code) => {
      const result = {
        stdout: Buffer.concat(stdout).toString("utf8"),
        stderr: Buffer.concat(stderr).toString("utf8"),
      };
      if (code === 0) finish(null, result);
      else finish(new Error(result.stderr.trim() || `${command} exited with code ${code}`));
    });
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      finish(new Error(`${command} timed out after ${Math.ceil(timeoutMs / 1000)} seconds`));
    }, timeoutMs);
    if (input) child.stdin.end(input);
    else child.stdin.end();
  });
}

function curlArgs(url, { body, timeoutMs }) {
  const args = [
    "--fail-with-body",
    "--silent",
    "--show-error",
    "--max-time",
    String(Math.max(1, Math.ceil(timeoutMs / 1000))),
    "--header",
    "Accept: application/json",
  ];
  if (body !== undefined) {
    args.push(
      "--request",
      "POST",
      "--header",
      "Content-Type: application/json",
      "--data-binary",
      "@-",
    );
  }
  args.push(url);
  return args;
}

function localHttpError(url, status, text = "", apiKey = "") {
  if (status === 401 || status === 403) {
    return new Error(`${url} returned HTTP ${status}: local API authentication failed. Enter a valid API key when registering the model, set the provider's API-key environment variable (e.g. OMLX_API_KEY), or configure pi for this same Base URL.`);
  }
  const detail = apiKey ? text.replaceAll(apiKey, "[redacted]") : text;
  return new Error(`${url} returned HTTP ${status}${detail ? `: ${detail.slice(0, 500)}` : ""}`);
}

async function curlJson(url, options = {}) {
  const timeoutMs = options.timeoutMs || DISCOVERY_TIMEOUT_MS;
  if (options.apiKey) {
    const response = await fetch(url, {
      method: options.body === undefined ? "GET" : "POST",
      headers: {
        Accept: "application/json",
        ...(options.body === undefined ? {} : { "Content-Type": "application/json" }),
        Authorization: `Bearer ${options.apiKey}`,
      },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      redirect: "error",
      signal: AbortSignal.timeout(timeoutMs),
    });
    const text = await response.text();
    if (!response.ok) throw localHttpError(url, response.status, text, options.apiKey);
    try {
      return JSON.parse(text);
    } catch {
      throw new Error(`${url} returned invalid JSON`);
    }
  }
  let stdout;
  try {
    ({ stdout } = await runCommand("curl", curlArgs(url, { ...options, timeoutMs }), {
      input: options.body === undefined ? undefined : JSON.stringify(options.body),
      timeoutMs: timeoutMs + 1000,
    }));
  } catch (error) {
    const status = error.message.match(/returned error: (\d{3})/)?.[1];
    if (status) throw localHttpError(url, Number(status));
    throw error;
  }
  try {
    return JSON.parse(stdout);
  } catch {
    throw new Error(`${url} returned invalid JSON`);
  }
}

function safeLocalBaseUrl(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("Base URL must be a valid HTTP URL");
  }
  const hostname = url.hostname.replace(/^\[|\]$/g, "");
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("Base URL must use HTTP or HTTPS");
  if (!["localhost", "127.0.0.1", "::1"].includes(hostname)) {
    throw new Error("Only loopback model endpoints can be registered");
  }
  url.pathname = url.pathname.replace(/\/+$/, "");
  url.search = "";
  url.hash = "";
  return url.toString().replace(/\/$/, "");
}

function sameLocalEndpoint(left, right) {
  try {
    return safeLocalBaseUrl(left) === safeLocalBaseUrl(right);
  } catch {
    return false;
  }
}

function resolvePiApiKey(value, env) {
  if (typeof value !== "string" || value.startsWith("!")) return "";
  let missing = false;
  const key = value.replace(/\$(\$|!|\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))/g,
    (_, reference, braced, bare) => {
      if (reference === "$" || reference === "!") return reference;
      const resolved = env[braced || bare];
      if (!resolved) missing = true;
      return resolved || "";
    }).trim();
  return !missing && key.length <= 4096 && !/[\r\n]/.test(key) ? key : "";
}

export async function resolveLocalApiKey(model, {
  providers = localProviders,
  env = process.env,
  piModelsPath = join((env.PI_CODING_AGENT_DIR || join(homedir(), ".pi", "agent"))
    .replace(/^~(?=\/|$)/, homedir()), "models.json"),
} = {}) {
  if (model.apiKey) return model.apiKey;
  const configured = providers.find((provider) => provider.apiKey
    && provider.protocol === model.protocol && sameLocalEndpoint(provider.baseUrl, model.baseUrl));
  if (configured) return configured.apiKey;
  if (model.protocol !== "openai-compatible") return "";
  let config;
  try {
    config = JSON.parse(await readFile(piModelsPath, "utf8"));
  } catch {
    return "";
  }
  for (const provider of Object.values(config?.providers || {})) {
    if (provider?.api !== "openai-completions" || !sameLocalEndpoint(provider.baseUrl, model.baseUrl)) continue;
    const key = resolvePiApiKey(provider.apiKey, env);
    if (key) return key;
  }
  return "";
}

function publicModel(model) {
  const { id, name, provider, protocol, model: modelId, mark, baseUrl } = model;
  return { id, name, provider, protocol, model: modelId, mark, baseUrl };
}

function registerModel(model, { manual = false } = {}) {
  const id = `${model.protocol}:${model.provider}:${model.model}`;
  const registered = { ...model, id };
  registry.set(id, registered);
  if (manual) manualRegistry.set(id, registered);
  return publicModel(registered);
}

function openAiModelIds(payload) {
  if (!Array.isArray(payload?.data)) throw new Error("Models response has no data array");
  return payload.data
    .filter((item) => item && typeof item.id === "string")
    .filter((item) => !["embedding", "embeddings"].includes(String(item.type || "").toLowerCase()))
    .filter((item) => !item.id.toLowerCase().startsWith("text-embedding-"))
    .map((item) => item.id);
}

export async function discoverLocalProvider(config) {
  const baseUrl = safeLocalBaseUrl(config.baseUrl);
  const apiKey = await resolveLocalApiKey({ ...config, baseUrl });
  const url = config.protocol === "ollama"
    ? `${baseUrl}/api/tags`
    : `${baseUrl.replace(/\/v1$/, "")}/v1/models`;
  const payload = await curlJson(url, { apiKey });
  const ids = config.protocol === "ollama"
    ? (payload.models || []).map((item) => item?.name || item?.model).filter(Boolean)
    : openAiModelIds(payload);
  return ids.filter((model) => !isAutoModel(model)).map((model) => registerModel({ ...config, baseUrl, apiKey, name: model, model }));
}

export function isAutoModel(model) {
  const values = typeof model === "string"
    ? [model]
    : [model?.name, model?.id, model?.model];
  return values.some((value) => {
    const text = String(value || "").trim().toLowerCase();
    return text === "auto" || text.split(/[:/]/).pop() === "auto";
  });
}

export function deduplicateModels(models) {
  const seen = new Set();
  const normalizeLabel = (value) => String(value || "").trim().replace(/\s+/g, " ").toLowerCase();
  return models.filter((model) => {
    const provider = normalizeLabel(model.provider);
    const name = normalizeLabel(model.name || model.model) || normalizeLabel(model.id);
    const protocol = normalizeLabel(model.protocol);
    const endpoint = String(model.baseUrl || "").trim();
    const key = JSON.stringify([provider, name, protocol, endpoint]);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function parseCopilotModels(output) {
  const trimmed = output.trim();
  if (!trimmed) return [];
  try {
    const parsed = JSON.parse(trimmed);
    const rows = Array.isArray(parsed) ? parsed : parsed.models;
    if (Array.isArray(rows)) {
      return rows
        .map((item) => typeof item === "string" ? item : item?.id || item?.name)
        .filter((item) => typeof item === "string" && item.trim() && !isAutoModel(item));
    }
  } catch {
    // The CLI may emit a plain-text model list.
  }
  return [...new Set(trimmed.split(/\r?\n/)
    .map((line) => line.replace(/^[\s*•-]+/, "").split(/\s{2,}/)[0].trim())
    .filter((line) => /^[A-Za-z0-9][A-Za-z0-9._:/-]+$/.test(line))
    .filter((line) => !isAutoModel(line)))];
}

async function discoverCopilot() {
  const client = new CopilotClient();
  try {
    await client.start();
    const models = await client.listModels();
    return models.filter((model) => !isAutoModel(model)).map((model) => registerModel({
      name: model.name || model.id,
      provider: "GitHub Copilot",
      protocol: "copilot-cli",
      model: model.id,
      mark: "C",
    }));
  } finally {
    await client.stop();
  }
}

export async function discoverModels() {
  registry.clear();
  const checks = [
    ...localProviders.map(async (provider) => ({
      provider: provider.provider,
      models: await discoverLocalProvider(provider),
    })),
    (async () => ({ provider: "GitHub Copilot", models: await discoverCopilot() }))(),
  ];
  const settled = await Promise.allSettled(checks);
  const models = [];
  const providers = settled.map((result, index) => {
    if (result.status === "fulfilled") {
      models.push(...result.value.models);
      return { provider: result.value.provider, available: true, count: result.value.models.length };
    }
    return {
      provider: index < localProviders.length ? localProviders[index].provider : "GitHub Copilot",
      available: false,
      count: 0,
      error: result.reason?.message || "Discovery failed",
    };
  });
  for (const model of manualRegistry.values()) {
    if (isAutoModel(model)) continue;
    registry.set(model.id, model);
    if (!models.some(({ id }) => id === model.id)) models.push(publicModel(model));
  }
  const selectable = deduplicateModels(models.filter((model) => !isAutoModel(model)));
  models.length = 0;
  models.push(...selectable);
  if (manualRegistry.size) {
    providers.push({ provider: "Manually registered", available: true, count: manualRegistry.size });
  }
  return { models, providers };
}

async function runLocalModel(model, prompt) {
  const baseUrl = safeLocalBaseUrl(model.baseUrl);
  const isOllama = model.protocol === "ollama";
  const url = isOllama ? `${baseUrl}/api/chat` : `${baseUrl}/chat/completions`;
  const payload = await curlJson(url, {
    timeoutMs: REQUEST_TIMEOUT_MS,
    apiKey: model.apiKey,
    body: { model: model.model, messages: [{ role: "user", content: prompt }], stream: false },
  });
  const text = isOllama ? payload?.message?.content : payload?.choices?.[0]?.message?.content;
  if (typeof text !== "string") throw new Error("The model returned no text content");
  return text;
}

async function runCopilotModel(model, prompt, outputPath) {
  const client = new CopilotClient();
  try {
    await client.start();
    const session = await client.createSession({
      model: model.model,
      workingDirectory: dirname(outputPath),
      infiniteSessions: { enabled: false },
      onPermissionRequest: () => ({
        kind: "reject",
        feedback: "Tools are disabled for arena responses. Return the answer directly.",
      }),
    });
    const response = await session.sendAndWait({ prompt }, REQUEST_TIMEOUT_MS);
    const text = response?.data?.content;
    if (typeof text !== "string" || !text.trim()) throw new Error("Copilot returned no output");
    return text.trim();
  } finally {
    await client.stop();
  }
}

function safeFilename(value) {
  return value.replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80) || "result";
}

async function executeModel(model, prompt) {
  const runDir = await mkdtemp(join(tmpdir(), "kilab-arena-"));
  try {
    const outputPath = join(runDir, `${safeFilename(model.model)}.txt`);
    const text = model.protocol === "copilot-cli"
      ? await runCopilotModel(model, prompt, outputPath)
      : await runLocalModel(model, prompt);
    await writeFile(outputPath, text, { encoding: "utf8", mode: 0o600 });
    const saved = await readFile(outputPath, "utf8");
    const token = basename(runDir);
    artifacts.set(token, runDir);
    setTimeout(() => {
      artifacts.delete(token);
      void rm(runDir, { recursive: true, force: true });
    }, 60 * 60 * 1000).unref();
    return { text: saved, artifact: `/api/artifacts/${encodeURIComponent(token)}/${encodeURIComponent(basename(outputPath))}` };
  } catch (error) {
    await rm(runDir, { recursive: true, force: true });
    throw error;
  }
}

async function cleanupArtifacts() {
  const directories = [...artifacts.values()];
  artifacts.clear();
  await Promise.allSettled(directories.map((directory) => rm(directory, { recursive: true, force: true })));
}

async function readJsonBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new Error("Request body is too large");
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new Error("Request body must be valid JSON");
  }
}

function sendJson(response, status, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
  response.end(body);
}

export async function handleRequest(request, response) {
  try {
    const url = new URL(request.url, "http://localhost");
    if (request.method === "GET" && url.pathname === "/") {
      const html = await readFile(join(APP_DIR, "index.html"));
      response.writeHead(200, {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": html.length,
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'self' https://cdn.tailwindcss.com; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com/lucide@latest https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js; style-src 'self' 'unsafe-inline'; frame-src 'self'; connect-src 'self'",
      });
      response.end(html);
      return;
    }
    if (request.method === "GET" && ["/app.js", "/styles.css"].includes(url.pathname)) {
      const content = await readFile(join(APP_DIR, basename(url.pathname)));
      response.writeHead(200, {
        "Content-Type": url.pathname.endsWith(".js") ? "text/javascript; charset=utf-8" : "text/css; charset=utf-8",
        "Content-Length": content.length,
        "X-Content-Type-Options": "nosniff",
      });
      response.end(content);
      return;
    }
    if (request.method === "GET" && url.pathname === "/api/models") {
      sendJson(response, 200, await discoverModels());
      return;
    }
    if (request.method === "POST" && url.pathname === "/api/models") {
      const body = await readJsonBody(request);
      if (!body || !["openai-compatible", "ollama"].includes(body.protocol)) {
        sendJson(response, 400, { error: "Choose an OpenAI-compatible or Ollama protocol" });
        return;
      }
      if (typeof body.model !== "string" || !body.model.trim()) {
        sendJson(response, 400, { error: "Model ID is required" });
        return;
      }
      let baseUrl;
      try {
        baseUrl = safeLocalBaseUrl(String(body.baseUrl || ""));
      } catch (error) {
        sendJson(response, 400, { error: error.message });
        return;
      }
      const suppliedApiKey = String(body.apiKey || "").trim();
      if (suppliedApiKey.length > 4096 || /[\r\n]/.test(suppliedApiKey)) {
        sendJson(response, 400, { error: "API key must be at most 4,096 characters and contain no line breaks" });
        return;
      }
      const apiKey = await resolveLocalApiKey({ baseUrl, protocol: body.protocol, apiKey: suppliedApiKey });
      const model = registerModel({
        name: String(body.name || body.model).trim().slice(0, 120),
        provider: String(body.provider || "Local model").trim().slice(0, 80),
        protocol: body.protocol,
        model: body.model.trim().slice(0, 200),
        baseUrl,
        apiKey,
        mark: String(body.mark || body.provider || "L").trim().slice(0, 1).toUpperCase(),
      }, { manual: true });
      sendJson(response, 201, { model });
      return;
    }
    if (request.method === "POST" && url.pathname === "/api/run") {
      const body = await readJsonBody(request);
      const prompt = typeof body?.prompt === "string" ? body.prompt.trim() : "";
      const model = registry.get(body?.modelId);
      if (!prompt || prompt.length > 100000) {
        sendJson(response, 400, { error: "Prompt must contain between 1 and 100,000 characters" });
        return;
      }
      if (!model) {
        sendJson(response, 404, { error: "Refresh models and select a registered model" });
        return;
      }
      sendJson(response, 200, await executeModel(model, prompt));
      return;
    }
    if (request.method === "GET" && url.pathname.startsWith("/api/artifacts/")) {
      const [, , , token, filename] = url.pathname.split("/");
      const directory = artifacts.get(token);
      if (!directory || !filename || basename(filename) !== filename) {
        sendJson(response, 404, { error: "Artifact not found" });
        return;
      }
      const content = await readFile(join(directory, filename));
      response.writeHead(200, {
        "Content-Type": "text/plain; charset=utf-8",
        "Content-Length": content.length,
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      response.end(content);
      return;
    }
    sendJson(response, 404, { error: "Not found" });
  } catch (error) {
    sendJson(response, 500, { error: error?.message || "Unexpected server error" });
  }
}

export function startServer(port = PORT) {
  const server = createServer((request, response) => {
    handleRequest(request, response);
  });
  server.on("close", () => {
    void cleanupArtifacts();
  });
  return server.listen(port, "127.0.0.1");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  startServer().on("listening", () => {
    console.log(`Blind LLM Arena running at http://127.0.0.1:${PORT}`);
  });
}
