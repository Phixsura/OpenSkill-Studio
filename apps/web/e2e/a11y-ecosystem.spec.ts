/**
 * axe-core WCAG 2.0 A/AA audit of the ecosystem pages (ADR-016, issue #35).
 *
 * Fails on serious/critical violations only (same bar as a11y-audit.spec.ts).
 * axe-core is injected from node_modules or /tmp/axe-tmp (see AXE_PATHS).
 */
import { existsSync, readFileSync } from "fs";

import { expect, test, type BrowserContext, type Page } from "@playwright/test";
import { loginInBrowser, registerUser, type AuthContext } from "./helpers";

const PASSWORD = process.env.E2E_TEST_PASSWORD || "TestPass123!";

const AXE_PATHS = ["node_modules/axe-core/axe.min.js", "/tmp/axe-tmp/package/axe.min.js"];

async function injectAxe(page: Page) {
  const found = AXE_PATHS.find((p) => existsSync(p));
  if (!found) throw new Error("axe-core unavailable — stage it at /tmp/axe-tmp");
  await page.addScriptTag({ content: readFileSync(found, "utf8") });
}

async function scan(page: Page, name: string) {
  await injectAxe(page);
  const results = await page.evaluate(async () => {
    // @ts-expect-error injected global
    return await window.axe.run(document, {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] },
    });
  });
  const serious = results.violations.filter(
    (v: { impact: string }) => v.impact === "serious" || v.impact === "critical",
  );
  if (serious.length) {
    console.log(`\n[a11y] ${name}: ${serious.length} serious/critical violations`);
    for (const v of serious) {
      console.log(`  - ${v.id}: ${v.help} (${v.nodes.length} nodes)`);
    }
  }
  return serious;
}

let auth: AuthContext;
let ctx: BrowserContext;
let page: Page;

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  auth = await registerUser(`Eco A11y${Date.now()}`);
  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, auth.email, PASSWORD);
});

test.afterAll(async () => {
  await ctx?.close();
});

const PAGES = [
  "/dashboard/ecosystem",
  "/dashboard/ecosystem/catalog",
  "/dashboard/ecosystem/changes",
  "/dashboard/ecosystem/discoveries",
  "/dashboard/ecosystem/pricing",
  "/dashboard/ecosystem/benchmarks",
  "/dashboard/ecosystem/compare",
  "/dashboard/ecosystem/sources",
  "/dashboard/ecosystem/security",
  "/dashboard/ecosystem/review",
  "/dashboard/ecosystem/components",
  "/dashboard/ecosystem/watchlists",
];

test("ecosystem pages have no serious/critical WCAG 2.0 A/AA violations", async () => {
  for (const path of PAGES) {
    await page.goto(path);
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(1200);
    expect(await scan(page, path), path).toHaveLength(0);
  }
});
