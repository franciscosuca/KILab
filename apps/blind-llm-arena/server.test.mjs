import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { test } from "node:test";
import { handleRequest, parseCopilotModels, startServer } from "./server.mjs";

test("parseCopilotModels supports JSON and plain text", () => {
  assert.deepEqual(parseCopilotModels('{"models":[{"id":"gpt-5"},{"name":"claude-sonnet"}]}'), [
    "gpt-5",
    "claude-sonnet",
  ]);
  assert.deepEqual(parseCopilotModels("- gpt-5\n* claude-sonnet\n"), ["gpt-5", "claude-sonnet"]);
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
      }),
    });
    const { model } = await registration.json();
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

function startServerFixture(handler) {
  return createServer(handler).listen(0, "127.0.0.1");
}
