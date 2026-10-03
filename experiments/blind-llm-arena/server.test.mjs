import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { deduplicateModels, discoverLocalProvider, handleRequest, isAutoModel, parseCopilotModels, resolveLocalApiKey, startServer } from "./server.mjs";

test("duplicate model entries are collapsed without merging different providers", () => {
  const models = [
    { id: "copilot:one", name: "Claude Opus 5.5", provider: "GitHub Copilot", model: "one" },
    { id: "copilot:two", name: " Claude  Opus 5.5 ", provider: "GitHub Copilot", model: "two" },
    { id: "local:one", name: "Claude Opus 5.5", provider: "Local runtime", model: "one" },
  ];
  assert.deepEqual(deduplicateModels(models).map(({ id }) => id), ["copilot:one", "local:one"]);
});

test("parseCopilotModels supports JSON and plain text", () => {
  assert.deepEqual(parseCopilotModels('{"models":[{"id":"gpt-5"},{"name":"claude-sonnet"}]}'), [
    "gpt-5",
    "claude-sonnet",
  ]);
  assert.deepEqual(parseCopilotModels("- gpt-5\n* claude-sonnet\n- auto\n"), ["gpt-5", "claude-sonnet"]);
  assert.equal(isAutoModel({ name: "Auto", id: "copilot-cli:GitHub Copilot:auto" }), true);
  assert.equal(isAutoModel({ name: "Claude Opus 5.5", id: "claude-opus-5.5" }), false);
});

test("server rejects non-loopback model registration", async () => {
  const server = startServer(0);
  await once(server, "listening");
  const { port } = server.address();
  try {
    const response = await fetch(`http://127.0.0.1:${port}/api/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        protocol: "openai-compatible",
        provider: "Remote",
        model: "example",
        baseUrl: "https://example.com/v1",
      }),
    });
    assert.equal(response.status, 400);
    assert.match((await response.json()).error, /loopback/);
  } finally {
    server.close();
  }
});

test("unknown routes return JSON 404 responses", async () => {
  const response = {
    status: 0,
    headers: {},
    body: "",
    writeHead(status, headers) {
      this.status = status;
      this.headers = headers;
    },
    end(body) {
      this.body = body;
    },
  };
  await handleRequest({ method: "GET", url: "/missing" }, response);
  assert.equal(response.status, 404);
  assert.deepEqual(JSON.parse(response.body), { error: "Not found" });
});

test("local runs use the registered model and expose the saved artifact", async () => {
  const modelServer = startServerFixture((request, response) => {
    assert.equal(request.url, "/v1/chat/completions");
    assert.equal(request.headers.authorization, "Bearer fixture-secret");
    response.writeHead(200, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ choices: [{ message: { content: "fixture response" } }] }));
  });
  const arenaServer = startServer(0);
  await Promise.all([once(modelServer, "listening"), once(arenaServer, "listening")]);
  const modelPort = modelServer.address().port;
  const arenaPort = arenaServer.address().port;
  try {
    const registration = await fetch(`http://127.0.0.1:${arenaPort}/api/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        protocol: "openai-compatible",
        provider: "Fixture",
        model: "fixture-model",
        baseUrl: `http://127.0.0.1:${modelPort}/v1`,
        apiKey: "fixture-secret",
      }),
    });
    const { model } = await registration.json();
    assert.equal(model.apiKey, undefined);
    const run = await fetch(`http://127.0.0.1:${arenaPort}/api/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modelId: model.id, prompt: "Test prompt" }),
    });
    assert.equal(run.status, 200);
    const result = await run.json();
    assert.equal(result.text, "fixture response");
    const artifact = await fetch(`http://127.0.0.1:${arenaPort}${result.artifact}`);
    assert.equal(await artifact.text(), "fixture response");
  } finally {
    modelServer.close();
    arenaServer.close();
  }
});

test("local keys prefer an explicit key, then the configured key for the same endpoint and protocol", async (t) => {
  const { path } = await piConfigFixture(t, {});
  const model = { protocol: "openai-compatible", baseUrl: "http://127.0.0.1:18000/v1" };
  const options = { providers: [{ ...model, apiKey: "environment-secret" }], piModelsPath: path };
  assert.equal(await resolveLocalApiKey({ ...model, apiKey: "manual-secret" }, options), "manual-secret");
  assert.equal(await resolveLocalApiKey({ ...model, apiKey: "" }, options), "environment-secret");
  assert.equal(await resolveLocalApiKey({ ...model, baseUrl: `${model.baseUrl}/` }, options), "environment-secret");
  assert.equal(await resolveLocalApiKey({ ...model, baseUrl: "http://127.0.0.1:18001/v1" }, options), "");
  assert.equal(await resolveLocalApiKey({ ...model, protocol: "ollama" }, options), "");
});

test("pi credentials are reused only for the exact loopback OpenAI-compatible endpoint", async (t) => {
  const model = { protocol: "openai-compatible", baseUrl: "http://127.0.0.1:18000/v1" };
  const { path } = await piConfigFixture(t, {
    omlx: { api: "openai-completions", baseUrl: `${model.baseUrl}/`, apiKey: "pi-secret" },
    remote: { api: "openai-completions", baseUrl: "https://example.com/v1", apiKey: "remote-secret" },
    anthropic: { api: "anthropic-messages", baseUrl: "http://127.0.0.1:18002/v1", apiKey: "other-secret" },
  });
  const options = { providers: [], piModelsPath: path, env: {} };
  assert.equal(await resolveLocalApiKey(model, options), "pi-secret");
  assert.equal(await resolveLocalApiKey({ ...model, apiKey: "manual-secret" }, options), "manual-secret");
  for (const baseUrl of [
    "http://localhost:18000/v1", "http://127.0.0.1:18001/v1", "http://127.0.0.1:18000/other",
    "https://example.com/v1", "http://127.0.0.1:18002/v1",
  ]) {
    assert.equal(await resolveLocalApiKey({ ...model, baseUrl }, options), "");
  }
  assert.equal(await resolveLocalApiKey({ ...model, protocol: "ollama" }, options), "");
  assert.equal(await resolveLocalApiKey(model, {
    ...options, providers: [{ ...model, apiKey: "environment-secret" }],
  }), "environment-secret");
});

test("pi key references resolve safely; missing configuration and shell commands are ignored", async (t) => {
  const model = { protocol: "openai-compatible", baseUrl: "http://127.0.0.1:18000/v1" };
  const { directory, path } = await piConfigFixture(t, {});
  const options = { providers: [], piModelsPath: path, env: { FIXTURE_KEY: "env-secret" } };
  const marker = join(directory, "must-not-exist");
  for (const [apiKey, expected] of [
    ["literal-secret", "literal-secret"], ["$FIXTURE_KEY", "env-secret"], ["${FIXTURE_KEY}", "env-secret"],
    ["prefix-${FIXTURE_KEY}", "prefix-env-secret"], ["$$dollar-$!bang", "$dollar-!bang"],
    ["$MISSING", ""], ["${MISSING}", ""], [`!touch '${marker}'`, ""],
    ["bad\nkey", ""], ["x".repeat(4097), ""], [null, ""],
  ]) {
    await writeFile(path, JSON.stringify({ providers: {
      omlx: { api: "openai-completions", baseUrl: model.baseUrl, apiKey },
    } }));
    assert.equal(await resolveLocalApiKey(model, options), expected);
  }
  await assert.rejects(readFile(marker), { code: "ENOENT" });
  await writeFile(path, "invalid json");
  assert.equal(await resolveLocalApiKey(model, options), "");
  await rm(path);
  assert.equal(await resolveLocalApiKey(model, options), "");
});

test("discovery and blank-key manual registration inherit pi credentials without exposing them", async (t) => {
  const received = [];
  const modelServer = startServerFixture((request, response) => {
    assert.equal(request.headers.authorization, "Bearer pi-fixture-secret");
    response.writeHead(200, { "Content-Type": "application/json" });
    if (request.url === "/v1/models") {
      response.end(JSON.stringify({ data: [{ id: "pi-fixture-model" }] }));
      return;
    }
    assert.equal(request.url, "/v1/chat/completions");
    let body = "";
    request.on("data", (chunk) => { body += chunk; });
    request.on("end", () => {
      received.push(JSON.parse(body));
      response.end(JSON.stringify({ choices: [{ message: { content: "pi fixture response" } }] }));
    });
  });
  const arenaServer = startServer(0);
  await Promise.all([once(modelServer, "listening"), once(arenaServer, "listening")]);
  const baseUrl = `http://127.0.0.1:${modelServer.address().port}/v1`;
  const arenaUrl = `http://127.0.0.1:${arenaServer.address().port}`;
  const { directory } = await piConfigFixture(t, {
    omlx: { api: "openai-completions", baseUrl, apiKey: "pi-fixture-secret" },
  });
  const previousPiDir = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = directory;
  try {
    const models = await discoverLocalProvider({ provider: "Fixture oMLX", protocol: "openai-compatible", baseUrl });
    assert.equal(models.length, 1);
    assert.equal(models[0].apiKey, undefined);
    assert.equal(JSON.stringify(models).includes("pi-fixture-secret"), false);
    const registration = await fetch(`${arenaUrl}/api/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider: "Local model", protocol: "openai-compatible", baseUrl: `${baseUrl}/`, model: "pi-fixture-model", apiKey: "" }),
    });
    assert.equal(registration.status, 201);
    const { model } = await registration.json();
    assert.equal(model.apiKey, undefined);
    for (const modelId of [models[0].id, model.id]) {
      const run = await fetch(`${arenaUrl}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ modelId, prompt: "Test inherited credentials" }),
      });
      assert.equal(run.status, 200);
      const result = await run.json();
      assert.equal(result.text, "pi fixture response");
      const artifact = await fetch(`${arenaUrl}${result.artifact}`);
      assert.equal(await artifact.text(), result.text);
    }
    assert.equal(received.length, 2);
    assert.equal(received.every((body) => body.model === "pi-fixture-model" && body.stream === false), true);
  } finally {
    if (previousPiDir === undefined) delete process.env.PI_CODING_AGENT_DIR;
    else process.env.PI_CODING_AGENT_DIR = previousPiDir;
    modelServer.close();
    arenaServer.close();
  }
});

test("local HTTP errors explain authentication failures and redact echoed API keys", async (t) => {
  const { directory } = await piConfigFixture(t, {});
  const previousPiDir = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = directory;
  let status = 401;
  const modelServer = startServerFixture((request, response) => {
    response.writeHead(status, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ error: request.headers.authorization || "API key required" }));
  });
  const arenaServer = startServer(0);
  await Promise.all([once(modelServer, "listening"), once(arenaServer, "listening")]);
  const arenaUrl = `http://127.0.0.1:${arenaServer.address().port}`;
  try {
    for (const apiKey of ["", "wrong-fixture-secret"]) {
      const registration = await fetch(`${arenaUrl}/api/models`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: "Auth fixture", protocol: "openai-compatible", baseUrl: `http://127.0.0.1:${modelServer.address().port}/v1`, model: "auth-fixture", apiKey }),
      });
      const { model } = await registration.json();
      for (status of [401, 403, 500]) {
        const run = await fetch(`${arenaUrl}/api/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ modelId: model.id, prompt: "Auth test" }),
        });
        assert.equal(run.status, 500);
        const { error } = await run.json();
        assert.match(error, new RegExp(`HTTP ${status}`));
        if (status !== 500) assert.match(error, /API key.*OMLX_API_KEY/);
        else if (apiKey) assert.match(error, /\[redacted\]/);
        assert.equal(error.includes("wrong-fixture-secret"), false);
      }
    }
  } finally {
    if (previousPiDir === undefined) delete process.env.PI_CODING_AGENT_DIR;
    else process.env.PI_CODING_AGENT_DIR = previousPiDir;
    modelServer.close();
    arenaServer.close();
  }
});

async function piConfigFixture(t, providers) {
  const directory = await mkdtemp(join(tmpdir(), "kilab-arena-pi-test-"));
  const path = join(directory, "models.json");
  await writeFile(path, JSON.stringify({ providers }), { mode: 0o600 });
  t.after(() => rm(directory, { recursive: true, force: true }));
  return { directory, path };
}

function startServerFixture(handler) {
  return createServer(handler).listen(0, "127.0.0.1");
}
