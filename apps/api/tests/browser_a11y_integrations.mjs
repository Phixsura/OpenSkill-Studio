/**
 * axe-core WCAG 2.1 A/AA audit of the five fabric pages (issue #43, R372).
 *
 * The functional walk checks accessible NAMES only; this runs the full
 * axe-core ruleset per page as an authenticated org admin and fails on
 * any serious/critical violation. Moderate/minor violations are printed
 * (report mode) so regressions are visible without blocking on upstream
 * design-system nits.
 *
 * Usage: web on :3000, api on :8000 (APP_ENV=test), then
 *   node tests/browser_a11y_integrations.mjs
 */
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE_SRC = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

const CHROMIUM_PATH =
  process.env.CHROMIUM_PATH ||
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;

const BASE = "http://localhost:3000";
let pass = 0,
  fail = 0;
const results = [];

function check(label, ok, detail = "") {
  if (ok) {
    pass++;
    results.push(`  ✅ ${label}`);
  } else {
    fail++;
    results.push(`  ❌ ${label}${detail ? ` — ${String(detail).slice(0, 220)}` : ""}`);
  }
}

const browser = await chromium.launch({
  headless: true,
  executablePath: CHROMIUM_PATH,
  args: ["--no-proxy-server"], // R367
});
const context = await browser.newContext({ viewport: { width: 1380, height: 900 } });
const page = await context.newPage();

const go = async (url) => {
  await page.goto(url, { waitUntil: "load", timeout: 90000 }); // R363: never networkidle
  await page.waitForTimeout(2200);
};

try {
  // ── auth bootstrap: register + org (same journey as the walk) ──
  await go(`${BASE}/register`);
  await page.fill("#displayName", "A11y Audit");
  await page.fill("#email", `a11y-${Date.now()}@test.com`);
  await page.fill("#password", "Test1234!");
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  const cont = await page.$('button:has-text("Continue to Dashboard")');
  if (cont) {
    await cont.click();
    await page.waitForTimeout(2000);
  }
  await go(`${BASE}/dashboard/orgs/new`);
  const nameField = await page.$(
    'input[id="name"], input[name="name"], input[placeholder*="name" i]',
  );
  await nameField.fill(`A11y Org ${Date.now()}`);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3500);
  const m = page.url().match(/orgs\/([0-9A-Z]{26})/);
  if (!m) throw new Error(`no orgId in url: ${page.url()}`);
  const intgBase = `${BASE}/dashboard/orgs/${m[1]}/integrations`;

  const pages = [
    ["register", `${BASE}/register`],
    ["login", `${BASE}/login`],
    ["hub", intgBase],
    ["identity", `${intgBase}/identity`],
    ["events", `${intgBase}/events`],
    ["sync", `${intgBase}/sync`],
    ["data", `${intgBase}/data`],
  ];

  for (const [label, url] of pages) {
    await go(url);
    await page.evaluate(AXE_SRC);
    const res = await page.evaluate(async () => {
      // WCAG 2.1 A + AA — the enterprise-procurement baseline (VPAT).
      return await window.axe.run(document, {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
        resultTypes: ["violations"],
      });
    });
    const blockers = res.violations.filter((v) => ["serious", "critical"].includes(v.impact));
    const advisory = res.violations.filter((v) => !["serious", "critical"].includes(v.impact));
    check(
      `${label}: zero serious/critical axe violations`,
      blockers.length === 0,
      blockers.map((v) => `${v.id}(${v.impact})×${v.nodes.length}`).join(", "),
    );
    for (const v of blockers.slice(0, 4)) {
      results.push(
        `       ↳ ${v.id}: ${v.help} — ${v.nodes[0]?.html?.slice(0, 120) ?? ""}`,
      );
    }
    if (advisory.length) {
      results.push(
        `     (advisory on ${label}: ${advisory.map((v) => `${v.id}×${v.nodes.length}`).join(", ")})`,
      );
    }
  }
} catch (err) {
  fail++;
  results.push(`  ❌ journey crashed — ${String(err).slice(0, 300)}`);
} finally {
  await browser.close();
}

console.log(results.join("\n"));
console.log(`\nPASS=${pass} FAIL=${fail}`);
process.exit(fail > 0 ? 1 : 0);
