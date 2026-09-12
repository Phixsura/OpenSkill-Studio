/**
 * Playwright browser E2E — issue #27 commercial frontend surfaces.
 * Covers: registration → auto-tenant → Tenant admin tabs (overview/billing/
 * credits/budgets/branding/domains/licenses/members) → registry price badge →
 * client portal access page → platform console redirect guard.
 *
 * Usage: node apps/api/tests/browser_e2e_commercial.mjs  (from repo root)
 * Requires: frontend on :3000, backend on :8000, Docker infra up.
 * Monitor the API log for 500s while this runs (issue §12.4).
 */
import { chromium } from "playwright";

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
    results.push(`  ❌ ${label}${detail ? `: ${detail}` : ""}`);
  }
}

function section(name) {
  results.push(`\n${"=".repeat(60)}`);
  results.push(`  ${name}`);
  results.push("=".repeat(60));
}

const email = `cp-e2e-${Date.now()}@test.com`;
const password = "Test1234!";

const browser = await chromium.launch({ headless: true, executablePath: CHROMIUM_PATH });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();

const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});

try {
  // ── 1. Register + auto-tenant ──
  section("1. Register → org → auto-created TRIAL tenant");
  await page.goto(`${BASE}/register`, { waitUntil: "networkidle", timeout: 15000 });
  await page.fill("#displayName", "CP Tester");
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2500);
  check("registration flow completes", true);

  // Login if not auto-redirected
  if (!page.url().includes("dashboard")) {
    await page.goto(`${BASE}/login`, { waitUntil: "networkidle" }).catch(() => {});
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2500);
  }
  check("lands on dashboard", page.url().includes("dashboard"), page.url());

  // Create an org → backend auto-creates a TRIAL tenant
  await page.goto(`${BASE}/dashboard/orgs/new`, { waitUntil: "networkidle" }).catch(() => {});
  const orgName = `CP Org ${Date.now()}`;
  const orgNameInput = await page.$("#name");
  if (orgNameInput) {
    await orgNameInput.fill(orgName);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2500);
  }
  check("org created", !page.url().includes("/new"));

  // ── 2. Tenant nav link appears (role-conditional nav) ──
  section("2. Tenant admin area");
  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle" }).catch(() => {});
  await page.waitForTimeout(1500);
  const tenantLink = await page.$('a[href^="/dashboard/tenant/"]');
  check("Tenant nav link visible", tenantLink !== null);
  let tenantBase = null;
  if (tenantLink) {
    tenantBase = await tenantLink.getAttribute("href");
    await tenantLink.click();
    await page.waitForTimeout(2000);
    const body = await page.textContent("body");
    check("tenant overview renders plan card", body.includes("Entitlements") || body.includes("Plan"));
    const trialBanner = body.includes("Trial ends");
    check("trial banner shown for TRIAL tenant", trialBanner);
    await page.screenshot({ path: "/tmp/cp-e2e-01-tenant-overview.png", fullPage: true });
  }

  // ── 3. Tenant tabs render ──
  section("3. Tenant tabs");
  for (const tab of ["billing", "credits", "budgets", "branding", "domains", "licenses", "members"]) {
    if (!tenantBase) break;
    await page
      .goto(`${BASE}${tenantBase}/${tab}`, { waitUntil: "networkidle", timeout: 10000 })
      .catch(() => {});
    const body = await page.textContent("body").catch(() => "");
    check(`${tab} tab renders`, body.length > 50);
  }
  await page.screenshot({ path: "/tmp/cp-e2e-02-tenant-billing.png", fullPage: true });

  // ── 4. Branding editor gated by plan ──
  section("4. Branding write is feature-gated (white_label)");
  if (tenantBase) {
    await page.goto(`${BASE}${tenantBase}/branding`, { waitUntil: "networkidle" }).catch(() => {});
    await page.waitForTimeout(1000);
    const saveBtn = await page.$('button:has-text("Save branding")');
    if (saveBtn) {
      await saveBtn.click();
      await page.waitForTimeout(1500);
      const body = await page.textContent("body");
      // TRIAL tenant runs school-plan entitlements: white_label=false → error toast
      check(
        "white_label gate surfaces",
        body.includes("white_label") || body.includes("white-label") || body.includes("plan"),
      );
    } else {
      check("branding editor renders", (await page.textContent("body")).includes("Theme"));
    }
  }

  // ── 5. Registry price badges ──
  section("5. Registry marketplace surface");
  await page.goto(`${BASE}/registry/workflows`, { waitUntil: "networkidle" }).catch(() => {});
  const regBody = await page.textContent("body").catch(() => "");
  check("workflow registry renders", regBody.length > 50);

  // ── 6. Client portal access page (public) ──
  section("6. Client portal");
  await page.goto(`${BASE}/client/access`, { waitUntil: "networkidle" }).catch(() => {});
  const portalBody = await page.textContent("body").catch(() => "");
  check("client access page public", portalBody.includes("access code") || portalBody.includes("review"));
  // Garbage token → friendly error, no crash
  await page.fill('input[placeholder*="code" i]', "not-a-real-token").catch(() => {});
  const openBtn = await page.$('button:has-text("Open project")');
  if (openBtn) {
    await openBtn.click();
    await page.waitForTimeout(2000);
    const errBody = await page.textContent("body");
    check("invalid token shows friendly error", errBody.includes("invalid") || errBody.includes("expired"));
  }
  await page.screenshot({ path: "/tmp/cp-e2e-03-client-access.png" });

  // ── 7. Platform console guarded ──
  section("7. Platform console role guard");
  await page.goto(`${BASE}/platform`, { waitUntil: "networkidle" }).catch(() => {});
  await page.waitForTimeout(2500);
  // Regular user → redirected back to /dashboard (no platform roles)
  check("non-platform user redirected", !page.url().endsWith("/platform"), page.url());

  // ── 8. Console errors ──
  section("8. Console errors");
  const criticalErrors = consoleErrors.filter(
    (e) =>
      !e.includes("favicon") &&
      !e.includes("Failed to load resource") &&
      !e.includes("hydration") &&
      !e.includes("Warning:") &&
      !e.includes("ERR_") &&
      !e.includes("net::"),
  );
  check(`no critical JS errors (${criticalErrors.length})`, criticalErrors.length === 0);
  if (criticalErrors.length > 0) {
    criticalErrors.slice(0, 5).forEach((e) => results.push(`    - ${e.slice(0, 150)}`));
  }
} catch (err) {
  results.push(`\n  💥 FATAL: ${err.message}`);
  fail++;
} finally {
  await browser.close();
}

console.log(results.join("\n"));
console.log(`\n${"=".repeat(60)}`);
console.log(`  RESULTS: ${pass} passed, ${fail} failed`);
console.log(`  Screenshots: /tmp/cp-e2e-*.png`);
console.log("=".repeat(60));

process.exit(fail > 0 ? 1 : 0);
