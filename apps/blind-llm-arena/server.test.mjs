import assert from "node:assert/strict";
import { once } from "node:events";
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
