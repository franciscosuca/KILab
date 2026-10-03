import assert from "node:assert/strict";
import { once } from "node:events";
import { test } from "node:test";
import { chromium, firefox } from "playwright";
import { startServer } from "./server.mjs";

const TAILWIND_URL = "https://cdn.tailwindcss.com/";
const LUCIDE_URL = "https://unpkg.com/lucide@latest";
const CONFETTI_URL = "https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js";
const SCRIPT_FIXTURES = {
  [TAILWIND_URL]: "document.head.insertAdjacentHTML('beforeend', '<style>.hidden{display:none}</style>');",
  [LUCIDE_URL]: "window.lucide = { createIcons() { document.documentElement.dataset.icons = 'ready'; } };",
  [CONFETTI_URL]: "window.confetti = () => { document.documentElement.dataset.confetti = 'ran'; };",
};

const INLINE_RESULT = `Here is the page:
\`\`\`html
<!doctype html><html><head><title>Inline fixture</title></head>
<body data-fixture="inline-fixture"><button id="action">Inline button</button>
<script>document.getElementById('action').onclick = () => { document.getElementById('action').textContent = 'Inline clicked'; };</script>
</body></html>
\`\`\``;

const EXTERNAL_RESULT = `<!doctype html><html><head><title>External fixture</title>
<script src="${TAILWIND_URL}"></script>
<script src="${LUCIDE_URL}"></script>
<script src="${CONFETTI_URL}"></script></head>
<body data-fixture="external-fixture"><button id="action">Run fixture</button>
<script>
  lucide.createIcons();
  document.getElementById('action').onclick = () => {
    confetti();
    document.getElementById('action').textContent = 'External clicked';
  };
  try { void parent.document.body; document.body.dataset.parentAccess = 'allowed'; }
  catch { document.body.dataset.parentAccess = 'blocked'; }
  fetch('/api/models').then(() => { document.body.dataset.network = 'allowed'; })
    .catch(() => { document.body.dataset.network = 'blocked'; });
</script></body></html>`;

for (const browserType of [chromium, firefox]) {
  const name = browserType.name();

  test(`${name}: preview buttons work, remain isolated, and preserve state across tab switches`, { timeout: 30000 }, async (t) => {
    const { page, libraryRequests, apiRequests, errors } = await harness(t, browserType, {
      "fixture-inline": INLINE_RESULT,
      "fixture-external": EXTERNAL_RESULT,
    });
    await runBenchmark(page, 2);
    const inline = cardFor(page, "inline-fixture");
    const external = cardFor(page, "external-fixture");
    await inline.getByRole("button", { name: "Preview", exact: true }).click();
    await external.getByRole("button", { name: "Preview", exact: true }).click();
    const inlineFrame = inline.locator("iframe").contentFrame();
    const externalFrame = external.locator("iframe").contentFrame();
    await inlineFrame.getByRole("button", { name: "Inline button", exact: true }).click();
    await externalFrame.getByRole("button", { name: "Run fixture", exact: true }).click();
    await inlineFrame.getByRole("button", { name: "Inline clicked", exact: true }).waitFor();
    await externalFrame.getByRole("button", { name: "External clicked", exact: true }).waitFor();
    await externalFrame.locator("html[data-icons='ready'][data-confetti='ran']").waitFor();
    await externalFrame.locator("body[data-parent-access='blocked'][data-network='blocked']").waitFor();
    await external.locator(".preview-status").waitFor({ state: "hidden" });
    assert.equal(await external.locator("iframe").getAttribute("sandbox"), "allow-scripts");
    assert.equal(apiRequests.length, 1, "preview must not call the model API");
    assert.deepEqual(libraryRequests.slice().sort(), Object.keys(SCRIPT_FIXTURES).sort());
    assert.deepEqual(errors, []);

    const requestCount = libraryRequests.length;
    await external.getByRole("button", { name: "Response", exact: true }).click();
    await external.getByRole("button", { name: "Preview", exact: true }).click();
    await external.getByRole("button", { name: "Preview", exact: true }).click();
    await externalFrame.getByRole("button", { name: "External clicked", exact: true }).waitFor();
    assert.equal(libraryRequests.length, requestCount, "tabs must not reload the frame or its libraries");

    await runBenchmark(page, 2);
    for (const card of await page.locator(".result-card").all()) {
      assert.equal(await card.locator('[data-view="response"]').getAttribute("aria-selected"), "true");
      assert.equal(await card.locator('[data-view="preview"]').getAttribute("aria-selected"), "false");
      assert.equal(await card.locator("iframe").isVisible(), false);
      assert.equal(await card.locator("iframe").getAttribute("srcdoc"), null);
      assert.equal(await card.locator(".preview-status").isVisible(), false);
    }
    const freshExternal = cardFor(page, "external-fixture");
    await freshExternal.getByRole("button", { name: "Preview", exact: true }).click();
    await freshExternal.locator("iframe").contentFrame().getByRole("button", { name: "Run fixture", exact: true }).waitFor();
  });

  test(`${name}: tall previews resize to expose controls without exceeding the height limit`, { timeout: 30000 }, async (t) => {
    const result = (marker, height) => `<!doctype html><html><body data-fixture="${marker}" style="margin:0">
      <div style="height:${height}px"></div><button>Visible control</button></body></html>`;
    const { page } = await harness(t, browserType, {
      "fixture-inline": result("tall-preview", 720),
      "fixture-external": result("bounded-preview", 5000),
    });
    await runBenchmark(page, 2);
    for (const card of await page.locator(".result-card").all()) {
      await card.getByRole("button", { name: "Preview", exact: true }).click();
    }
    await page.waitForFunction(() => [...document.querySelectorAll("iframe.preview")].every((frame) => frame.clientHeight >= 720));
    const tall = cardFor(page, "tall-preview");
    const tallHeight = await tall.locator("iframe").evaluate((frame) => frame.clientHeight);
    assert(tallHeight >= 720 && tallHeight <= 900);
    assert.equal(await cardFor(page, "bounded-preview").locator("iframe").evaluate((frame) => frame.clientHeight), 900);
    assert.equal(await tall.locator(".card-body").evaluate((body) => body.scrollHeight <= body.clientHeight + 1), true);
    const button = tall.locator("iframe").contentFrame().getByRole("button", { name: "Visible control", exact: true });
    const bounds = await button.boundingBox();
    const frameBounds = await tall.locator("iframe").boundingBox();
    assert(bounds.y + bounds.height <= frameBounds.y + frameBounds.height, "control must fit inside the frame before scrolling");
  });

  test(`${name}: slow libraries display a loading message rather than an unexplained blank preview`, { timeout: 30000 }, async (t) => {
    const { page } = await harness(t, browserType, { "fixture-external": EXTERNAL_RESULT });
    let release;
    const pending = new Promise((resolve) => { release = resolve; });
    await page.route(TAILWIND_URL, async (route) => {
      await pending;
      await route.fulfill({ contentType: "text/javascript", body: SCRIPT_FIXTURES[TAILWIND_URL] }).catch(() => {});
    });
    try {
      await runBenchmark(page, 1);
      const card = cardFor(page, "external-fixture");
      await card.getByRole("button", { name: "Preview", exact: true }).click();
      await card.locator(".preview-status").waitFor({ state: "visible" });
      assert.match(await card.locator(".preview-status").textContent(), /Loading interactive preview/);
      release();
      await card.locator("iframe").contentFrame().getByRole("button", { name: "Run fixture", exact: true }).waitFor();
      await card.locator(".preview-status").waitFor({ state: "hidden" });
    } finally {
      release();
    }
  });

  test(`${name}: unavailable libraries report the failure even after the frame finishes loading`, { timeout: 30000 }, async (t) => {
    const response = `<!doctype html><html><head><script src="${LUCIDE_URL}"></script></head>
      <body data-fixture="missing-library"><button>Generated button</button><script>lucide.createIcons();</script></body></html>`;
    const { page } = await harness(t, browserType, { "fixture-inline": response });
    await page.route(LUCIDE_URL, (route) => route.fulfill({ status: 503, contentType: "text/javascript", body: "// unavailable" }));
    await runBenchmark(page, 1);
    const card = cardFor(page, "missing-library");
    await card.getByRole("button", { name: "Preview", exact: true }).click();
    await frameLoaded(card);
    await card.locator(".preview-status.error").waitFor({ state: "visible" });
    assert.match(await card.locator(".preview-status").textContent(), /Preview issue: Could not load https:\/\/unpkg\.com\/lucide@latest/);
    assert.equal(await card.locator(".status b").textContent(), "Ready", "a preview error must not discard the model response");
  });

  test(`${name}: unapproved scripts are blocked and the reason is visible`, { timeout: 30000 }, async (t) => {
    const source = "https://example.invalid/not-allowed.js";
    const response = `<!doctype html><html><head><script src="${source}"></script></head>
      <body data-fixture="blocked-library"><button>Generated button</button></body></html>`;
    const { page } = await harness(t, browserType, { "fixture-inline": response });
    let requested = false;
    await page.route(source, (route) => {
      requested = true;
      return route.fulfill({ contentType: "text/javascript", body: "window.unapproved = true;" });
    });
    await runBenchmark(page, 1);
    const card = cardFor(page, "blocked-library");
    await card.getByRole("button", { name: "Preview", exact: true }).click();
    await frameLoaded(card);
    await card.locator(".preview-status.error").waitFor({ state: "visible" });
    assert.match(await card.locator(".preview-status").textContent(), /Could not load https:\/\/example\.invalid\/not-allowed\.js/);
    assert.equal(requested, false, "unapproved scripts must never be fetched");
  });
}

function cardFor(page, marker) {
  return page.locator(".result-card").filter({ has: page.locator(".response").filter({ hasText: marker }) });
}

async function frameLoaded(card) {
  await card.locator("iframe").contentFrame().locator("body").evaluate(() => new Promise((resolve) => {
    if (document.readyState !== "loading") setTimeout(resolve, 0);
    else addEventListener("DOMContentLoaded", () => setTimeout(resolve, 0), { once: true });
  }));
}

async function runBenchmark(page, count) {
  await page.locator("#run-button").click();
  await page.waitForFunction((count) => document.querySelector("#run-summary").textContent.startsWith(`${count} ready`)
    && !document.querySelector("#run-button").disabled, count);
}

async function harness(t, browserType, responses) {
  const server = startServer(0);
  await once(server, "listening");
  let browser;
  t.after(async () => {
    await browser?.close();
    await new Promise((resolve) => server.close(resolve));
  });
  browser = await browserType.launch({ headless: true });
  const page = await browser.newPage();
  page.setDefaultTimeout(5000);
  const libraryRequests = [];
  const apiRequests = [];
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  for (const [source, body] of Object.entries(SCRIPT_FIXTURES)) {
    await page.route(source, (route) => {
      libraryRequests.push(source);
      return route.fulfill({ contentType: "text/javascript", body });
    });
  }
  const models = Object.keys(responses).map((id, index) => ({ id, name: `Fixture ${index + 1}`, provider: "Test fixture" }));
  await page.route("**/api/models", (route) => {
    apiRequests.push(route.request().url());
    return route.fulfill({ json: { models, providers: [{ provider: "Test fixture", available: true, count: models.length }] } });
  });
  await page.route("**/api/run", (route) => route.fulfill({ json: { text: responses[route.request().postDataJSON().modelId] } }));
  await page.goto(`http://127.0.0.1:${server.address().port}`);
  for (const model of models) await page.getByRole("checkbox", { name: new RegExp(model.name) }).check();
  await page.getByRole("switch", { name: "Use mock responses" }).click();
  return { page, libraryRequests, apiRequests, errors };
}
