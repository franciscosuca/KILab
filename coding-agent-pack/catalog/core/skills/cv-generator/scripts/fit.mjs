// Fit the CV on one A4 page and export a PDF.
// Usage: node fit.mjs <cv.html> [out.pdf]
// Picks the largest body font size (9.0 -> 7.8pt) at which both columns fit, writes it back into the HTML,
// then prints a PDF. Exit code 2 = content too long even at the minimum size (trim text, see SKILL.md).
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const html = resolve(process.argv[2] ?? "");
const pdf = resolve(process.argv[3] ?? html.replace(/\.html?$/, ".pdf"));
const require = createRequire(resolve(process.env.CV_PW_DIR ?? "./") + "/");
const { chromium } = require("playwright");

const MAX = 9.0, MIN = 7.8, STEP = 0.05, BOTTOM_PAD_MM = 3;

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(html).href);

const measure = (fs) =>
  page.evaluate((fs) => {
    document.documentElement.style.setProperty("--fs", `${fs}pt`);
    const pg = document.querySelector(".page").getBoundingClientRect();
    const mmPx = 96 / 25.4;
    const bottom = (el) => el.getBoundingClientRect().bottom - pg.top;
    const main = bottom(document.querySelector(".content")); // border-box: already includes its bottom padding
    const side = bottom([...document.querySelectorAll("aside > *")].pop()) + 5 * mmPx;
    const limit = pg.height - 3 * mmPx;
    return { over: Math.max(main, side) - limit, main, side, limit };
  }, fs);

let chosen = null, last = null;
for (let fs = MAX; fs >= MIN - 1e-9; fs -= STEP) {
  last = await measure(fs);
  if (last.over <= 0) { chosen = Math.round(fs * 100) / 100; break; }
}

if (chosen === null) {
  const px = Math.ceil(last.over), mm = (px * 25.4 / 96).toFixed(1);
  console.error(`DOES NOT FIT: content overflows by ~${px}px (~${mm}mm, about ${Math.ceil(px / 15)} lines) at ${MIN}pt. Trim text and re-run.`);
  await browser.close();
  process.exit(2);
}

await measure(chosen);
let src = readFileSync(html, "utf8");
src = src.replace(/--fs:\s*[\d.]+pt;/, `--fs: ${chosen}pt;`);
writeFileSync(html, src);

await page.goto(pathToFileURL(html).href);
await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
const slack = (await measure(chosen)).over;
console.log(JSON.stringify({ fontSizePt: chosen, slackPx: Math.round(-slack), pdf }));
await browser.close();
