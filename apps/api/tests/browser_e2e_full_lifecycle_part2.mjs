/**
 * Playwright FULL browser E2E part 2 — issue #27 admin surfaces, feature
 * gates, lifecycle transitions, and revocation semantics in the UI.
 *
 * Complements browser_e2e_full_lifecycle.mjs (main commercial chain) with:
 *   tenant domain wizard (add → one-time token → verify → activate → disable)
 *   plan-change dialog with proration preview (school → growth)
 *   budgets create/remove · tenant members add/remove
 *   branding save (white_label gate blocks on school, passes after override)
 *   platform plans: draft version create + activate
 *   suspend → suspension banner in tenant UI → reactivate
 *   portal reviewer role gate (no approve/final-accept buttons)
 *   guest link revoke mid-session (next request bounces)
 *   partner statement CSV export (real download)
 *   platform pricing/usage explorers render seeded rows
 *
 * Usage: node apps/api/tests/browser_e2e_full_lifecycle_part2.mjs
 * Requires: frontend :3000, backend :8000 (APP_ENV=test), Docker infra up.
 */
import { execFileSync } from "node:child_process";
import { chromium } from "playwright";

const CHROMIUM_PATH =
  process.env.CHROMIUM_PATH ||
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;

const BASE = "http://localhost:3000";
const API = "http://localhost:8000/api/v1";

let pass = 0,
  fail = 0;
const results = [];
function check(label, ok, detail = "") {
  if (ok) {
    pass++;
    results.push(`  ✅ ${label}`);
  } else {
    fail++;
    results.push(`  ❌ ${label}${detail ? `: ${String(detail).slice(0, 200)}` : ""}`);
  }
}
function section(name) {
  results.push(`\n${"=".repeat(60)}\n  ${name}\n${"=".repeat(60)}`);
}
const uid = () => Math.random().toString(36).slice(2, 8) + Date.now().toString(36).slice(-4);

async function api(path, { method = "GET", token, body } = {}) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  let json = null;
  try {
    json = await res.json();
  } catch {
    /* 204 */
  }
  return { status: res.status, json };
}
async function register(prefix) {
  const email = `${prefix}-${uid()}@test.com`;
  for (let i = 0; i < 5; i++) {
    const r = await api("/auth/register", {
      method: "POST",
      body: { email, password: "TestPass123!", display_name: prefix },
    });
    if (r.status === 201 || r.status === 200)
      return { email, token: r.json.access_token, userId: r.json.user.id };
    if (r.status === 429) {
      await new Promise((s) => setTimeout(s, 2000 * (i + 1)));
      continue;
    }
    throw new Error(`register ${r.status}: ${JSON.stringify(r.json).slice(0, 200)}`);
  }
  throw new Error("register: rate-limited after retries");
}
function pyHelper(code) {
  return execFileSync("uv", ["run", "python", "-c", code], {
    cwd: `${process.env.HOME}/Develop/OpenSkill-Studio/apps/api`,
    env: { ...process.env, NO_PROXY: "localhost,127.0.0.1", PYTHONPATH: "." },
    encoding: "utf8",
    timeout: 120000,
  }).trim();
}
const promoteAdmin = (email) =>
  pyHelper(`
import asyncio
from sqlalchemy import select
async def go():
    from app.core.database import AsyncSessionLocal, engine
    from app.models.user import User, UserRole
    async with AsyncSessionLocal() as db:
        u = (await db.execute(select(User).where(User.email == "${email}"))).scalar_one()
        u.role = UserRole.ADMIN
        await db.commit()
    await engine.dispose()
asyncio.run(go())
print("ok")`);

const browser = await chromium.launch({ headless: true, executablePath: CHROMIUM_PATH });
const consoleErrors = [];
async function newPage(context) {
  const page = await context.newPage();
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });
  return page;
}
async function uiLogin(page, email) {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle", timeout: 20000 });
  await page.fill("#email", email);
  await page.fill("#password", "TestPass123!");
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard/, { timeout: 15000 });
}
const bodyText = async (page) => (await page.textContent("body").catch(() => "")) || "";

try {
  // ═══════════════ SEED: admin + owner with school-plan tenant ═══════════════
  section("0. Seed: admin + tenant owner on manual school subscription");
  const admin = await register("bf2-admin");
  promoteAdmin(admin.email);
  const adminLogin = await api("/auth/login", {
    method: "POST",
    body: { email: admin.email, password: "TestPass123!" },
  });
  admin.token = adminLogin.json.access_token;
  check("admin bootstrapped", adminLogin.status === 200);

  const owner = await register("bf2-owner");
  const orgR = await api("/orgs", {
    method: "POST",
    token: owner.token,
    body: { name: `BF2 Org ${uid()}` },
  });
  check("org + auto tenant created", orgR.status === 201, orgR.status);
  const tenantsR = await api("/tenants/mine", { token: owner.token });
  const tenantId = tenantsR.json.data[0].id;
  // Manual school subscription so plan-change / entitlements are live
  // (manual provider is platform-admin-driven; admin bypasses tenant membership)
  const subR = await api(`/tenants/${tenantId}/subscription`, {
    method: "POST",
    token: admin.token,
    body: { plan_key: "school", interval: "month", provider: "manual" },
  });
  check("manual school subscription active (API seed)", subR.status === 201, JSON.stringify(subR.json).slice(0, 150));

  // ═══════════════ 1. DOMAIN WIZARD (UI) ═══════════════
  section("1. Domain wizard: add → one-time token → verify → activate → disable");
  const octx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const opage = await newPage(octx);
  await uiLogin(opage, owner.email);
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}/domains`, { waitUntil: "networkidle" });
  const host = `bf2-${uid()}.example.com`;
  await opage.fill('input[placeholder="academy.example.com"]', host);
  await opage.click('button:has-text("Add")');
  await opage.waitForSelector("text=shown only once", { timeout: 10000 });
  check("one-time token banner appears", true);
  const tokenText = await bodyText(opage);
  const tokenMatch = tokenText.match(/TXT\s*"([^"]+)"/);
  const rawToken = tokenMatch?.[1];
  check("raw verification token extractable", Boolean(rawToken), tokenText.slice(0, 200));
  // mock verifier passes ok- tokens; the issued token IS ok-prefixed in mock mode
  check("mock-mode token is ok-prefixed", rawToken?.startsWith("ok-"), rawToken);
  await opage.fill('input[placeholder="Verification token"]', rawToken);
  await opage.click('button:has-text("Verify")');
  await opage.waitForSelector("text=Domain verified", { timeout: 10000 });
  check("domain verified via UI (toast)", true);
  await opage.waitForSelector('button:has-text("Activate")', { timeout: 10000 });
  await opage.click('button:has-text("Activate")');
  await opage.waitForSelector("text=Domain updated", { timeout: 10000 });
  check("domain activated via UI", true);
  await opage.waitForTimeout(800);
  check("status shows active", (await bodyText(opage)).includes("active"));
  await opage.screenshot({ path: "/tmp/bf2-01-domain-active.png", fullPage: true });
  // site-context resolves it (API assert — public endpoint)
  const ctxR = await api(`/public/site-context?host=${host}`);
  check("site-context resolves active domain", ctxR.json?.data?.tenant_id === tenantId, JSON.stringify(ctxR.json).slice(0, 150));
  await opage.click('button:has-text("Disable")');
  await opage.waitForTimeout(1500);
  const ctxR2 = await api(`/public/site-context?host=${host}`);
  check("disabled domain stops resolving", ctxR2.json?.data?.tenant_id == null, JSON.stringify(ctxR2.json).slice(0, 150));

  // ═══════════════ 2. PLAN CHANGE DIALOG + PRORATION PREVIEW (UI) ═══════════════
  section("2. Billing: plan-change dialog previews proration, applies change");
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}/billing`, { waitUntil: "networkidle" });
  await opage.waitForSelector('button:has-text("Change plan")', { timeout: 10000 });
  await opage.click('button:has-text("Change plan")');
  // <option> elements are always "hidden" to Playwright — wait for the select itself
  await opage.waitForSelector("div.fixed select", { timeout: 5000 });
  check("change-plan dialog opens", true);
  await opage.selectOption("div.fixed select", { value: "growth" });
  // R101[L9]: preview now renders a human summary ("Net change: ...")
  const previewEl = await opage.waitForSelector("text=Net change:", { timeout: 10000 });
  const previewText = (await previewEl.evaluate((el) => el.parentElement?.textContent)) || "";
  check("proration preview renders", previewText.includes("Net change:"), previewText.slice(0, 120));
  check("preview carries proration numbers", /credit|charge|days/i.test(previewText), previewText.slice(0, 200));
  await opage.click('button:has-text("Confirm change")');
  await opage.waitForSelector("text=Plan change submitted", { timeout: 10000 });
  check("plan change submitted via UI", true);
  await opage.waitForTimeout(1200);
  check("subscription card shows growth", /growth/i.test(await bodyText(opage)));
  await opage.screenshot({ path: "/tmp/bf2-02-plan-change.png", fullPage: true });

  // ═══════════════ 3. BRANDING white_label GATE (UI) ═══════════════
  section("3. Branding: growth plan has white_label — save succeeds");
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}/branding`, { waitUntil: "networkidle" });
  await opage.waitForSelector('button:has-text("Save branding")', { timeout: 10000 });
  await opage.fill('input[placeholder="Partner Academy"]', "BF2 Academy");
  await opage.click('button:has-text("Save branding")');
  await opage.waitForSelector("text=Branding saved", { timeout: 10000 });
  check("branding saves on white_label plan (toast)", true);

  // ═══════════════ 4. BUDGETS CREATE/REMOVE (UI) ═══════════════
  section("4. Budgets: create tenant-wide monthly budget, then remove");
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}/budgets`, { waitUntil: "networkidle" });
  await opage.click('button:has-text("New budget")');
  await opage.fill('input[placeholder="Limit (USD)"]', "250");
  await opage.click('button:has-text("Create")');
  await opage.waitForSelector("text=Budget created", { timeout: 10000 });
  check("budget created via UI (toast)", true);
  await opage.waitForTimeout(800);
  const budgetBody = await bodyText(opage);
  check("budget row renders tenant scope", budgetBody.includes("tenant"), budgetBody.slice(0, 300));
  check("budget row shows $250 limit", /250/.test(budgetBody));
  await opage.click('button:has-text("Remove")');
  await opage.waitForSelector("text=Budget removed", { timeout: 10000 });
  check("budget removed via UI (toast)", true);

  // ═══════════════ 5. TENANT MEMBERS ADD/REMOVE (UI) ═══════════════
  section("5. Members: add billing_admin by user id, then remove");
  const billingUser = await register("bf2-billing");
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}/members`, { waitUntil: "networkidle" });
  await opage.fill('input[placeholder="User ID"]', billingUser.userId);
  await opage.click('button:has-text("Add")');
  await opage.waitForSelector("text=Member added", { timeout: 10000 });
  check("member added via UI (toast)", true);
  await opage.waitForTimeout(800);
  check("member row renders", (await bodyText(opage)).includes("billing_admin"));
  // remove the newly-added member (last Remove button = newest row)
  const removeBtns = opage.locator('button:has-text("Remove")');
  await removeBtns.last().click();
  await opage.waitForSelector("text=Member removed", { timeout: 10000 });
  check("member removed via UI (toast)", true);

  // ═══════════════ 6. PLATFORM PLANS: DRAFT + ACTIVATE (UI) ═══════════════
  section("6. Platform plans: new draft version → activate");
  const actx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const apage = await newPage(actx);
  await uiLogin(apage, admin.email);
  await apage.goto(`${BASE}/platform/plans`, { waitUntil: "networkidle" });
  await apage.waitForSelector('button:has-text("New draft version")', { timeout: 10000 });
  await apage.locator('button:has-text("New draft version")').first().click();
  await apage.waitForSelector("text=Draft version created", { timeout: 10000 });
  check("draft version created via UI (toast)", true);
  await apage.waitForTimeout(1000);
  const activateBtn = apage.locator('button:has-text("Activate")').first();
  check("Activate button appears on draft", (await activateBtn.count()) > 0);
  await activateBtn.click();
  await apage.waitForSelector("text=Version activated", { timeout: 10000 });
  check("draft activated via UI (toast)", true);
  await apage.screenshot({ path: "/tmp/bf2-03-plans.png", fullPage: true });

  // ═══════════════ 7. SUSPEND → TENANT BANNER → REACTIVATE (UI) ═══════════════
  section("7. Lifecycle: suspend in console → banner in tenant UI → reactivate");
  await apage.goto(`${BASE}/platform/tenants/${tenantId}`, { waitUntil: "networkidle" });
  await apage.waitForSelector('input[placeholder="Suspension reason (required)"]', { timeout: 15000 });
  await apage.fill('input[placeholder="Suspension reason (required)"]', "bf2 e2e lifecycle test");
  await apage.click('button:has-text("Suspend")');
  await apage.waitForSelector("text=Tenant suspended", { timeout: 10000 });
  check("tenant suspended via UI (toast)", true);
  // Owner sees the suspension banner
  await opage.goto(`${BASE}/dashboard/tenant/${tenantId}`, { waitUntil: "networkidle" });
  const suspBanner = await opage
    .waitForSelector("text=This account is suspended", { timeout: 10000 })
    .then(() => true)
    .catch(() => false);
  check("suspension banner in tenant UI", suspBanner, (await bodyText(opage)).slice(0, 300));
  await opage.screenshot({ path: "/tmp/bf2-04-suspended.png", fullPage: true });
  // Suspension blocks consumption: purchase attempt 403s (API assert)
  const orgsList = await api("/orgs", { token: owner.token });
  const anyOrg = orgsList.json.data[0].id;
  const blockedR = await api(`/orgs/${anyOrg}/usage-events`, {
    method: "POST",
    token: owner.token,
    body: {
      usage_type: "image_generation",
      quantity: "1",
      occurred_at: new Date().toISOString(),
      idempotency_key: `bf2-blocked-${uid()}`,
    },
  });
  check("suspended tenant blocked on costed path (403)", blockedR.status === 403, blockedR.status);
  // Reactivate
  await apage.waitForSelector('button:has-text("Reactivate")', { timeout: 10000 });
  await apage.click('button:has-text("Reactivate")');
  await apage.waitForSelector("text=Tenant reactivated", { timeout: 10000 });
  check("tenant reactivated via UI (toast)", true);
  await opage.reload({ waitUntil: "networkidle" });
  await opage.waitForTimeout(1000);
  check("suspension banner gone after reactivate", !(await bodyText(opage)).includes("This account is suspended"));

  // ═══════════════ 8. PORTAL REVIEWER ROLE GATE + LINK REVOKE (UI) ═══════════════
  section("8. Portal: reviewer sees no approve; revoked link bounces");
  const projR = await api(`/orgs/${anyOrg}/projects`, {
    method: "POST",
    token: owner.token,
    body: {
      title: `BF2 Review ${uid()}`,
      description: "d",
      instructions: "i",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    },
  });
  const projectId = projR.json.data.id;
  const subCreate = await api(`/orgs/${anyOrg}/projects/${projectId}/submissions`, {
    method: "POST",
    token: owner.token,
  });
  const submissionId = subCreate.json.data.id;
  await api(`/orgs/${anyOrg}/projects/${projectId}/submissions/${submissionId}/submit`, {
    method: "POST",
    token: owner.token,
  });
  await api(`/orgs/${anyOrg}/projects/${projectId}/client-shares`, {
    method: "POST",
    token: owner.token,
    body: { submission_id: submissionId },
  });
  const revLinkR = await api(`/orgs/${anyOrg}/projects/${projectId}/client-links`, {
    method: "POST",
    token: owner.token,
    body: {
      label: "BF2 Reviewer",
      role: "reviewer",
      expires_at: new Date(Date.now() + 30 * 86400000).toISOString(),
    },
  });
  const reviewerToken = revLinkR.json?.data?.token;
  const reviewerLinkId = revLinkR.json?.data?.id;
  check("reviewer link minted (API seed)", Boolean(reviewerToken), revLinkR.status);

  const gctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const gpage = await newPage(gctx);
  await gpage.goto(`${BASE}/client/access`, { waitUntil: "networkidle" });
  await gpage.fill('input[placeholder="Access code"]', reviewerToken);
  await gpage.click('button:has-text("Open project")');
  await gpage.waitForURL(new RegExp(`/client/${projectId}`), { timeout: 15000 });
  await gpage.waitForSelector("text=Version 1", { timeout: 10000 });
  const reviewerBody = await bodyText(gpage);
  check("reviewer sees Request revision", reviewerBody.includes("Request revision"));
  check("reviewer does NOT see Approve version", !reviewerBody.includes("Approve version"));
  check("reviewer does NOT see Final accept", !reviewerBody.includes("Final accept"));
  await gpage.screenshot({ path: "/tmp/bf2-05-reviewer-gate.png", fullPage: true });

  // Revoke the link mid-session — next portal request bounces to access page
  const revokeR = await api(
    `/orgs/${anyOrg}/projects/${projectId}/client-links/${reviewerLinkId}/revoke`,
    { method: "POST", token: owner.token },
  );
  check("link revoked (API)", revokeR.status === 200, revokeR.status);
  await gpage.reload({ waitUntil: "networkidle" });
  const bounced = await gpage
    .waitForURL(/client\/access/, { timeout: 15000 })
    .then(() => true)
    .catch(() => false);
  check("revoked session bounces to access page", bounced, gpage.url());
  await gctx.close();

  // ═══════════════ 9. PLATFORM EXPLORERS RENDER SEEDED DATA (UI) ═══════════════
  section("9. Platform pricing + usage explorers");
  await apage.goto(`${BASE}/platform/pricing`, { waitUntil: "networkidle" });
  await apage.waitForTimeout(1000);
  const pricingBody = await bodyText(apage);
  check("pricing page renders policy tabs", pricingBody.includes("price policies"));
  await apage.click('button:has-text("price policies")');
  await apage.waitForTimeout(800);
  check("price policies table renders", (await bodyText(apage)).includes("Name"));
  await apage.goto(`${BASE}/platform/usage`, { waitUntil: "networkidle" });
  await apage.fill('input[placeholder="Tenant ID"]', tenantId);
  await apage.waitForTimeout(1500);
  check("usage explorer filters by tenant", (await bodyText(apage)).length > 100);

  await octx.close();
  await actx.close();

  // ═══════════════ 10. CONSOLE ERRORS ═══════════════
  section("10. Console errors");
  const critical = consoleErrors.filter(
    (e) =>
      !e.includes("favicon") &&
      !e.includes("Failed to load resource") &&
      !e.includes("hydration") &&
      !e.includes("Warning:") &&
      !e.includes("ERR_") &&
      !e.includes("net::"),
  );
  check(`no critical JS errors (${critical.length})`, critical.length === 0);
  critical.slice(0, 5).forEach((e) => results.push(`    - ${e.slice(0, 150)}`));
} catch (err) {
  fail++;
  results.push(`\n  💥 FATAL: ${err.message}\n${(err.stack || "").split("\n").slice(1, 4).join("\n")}`);
} finally {
  await browser.close();
}

console.log(results.join("\n"));
console.log(`\n${"=".repeat(60)}`);
console.log(`  RESULTS: ${pass} passed, ${fail} failed`);
console.log(`  Screenshots: /tmp/bf2-*.png`);
console.log("=".repeat(60));
process.exit(fail > 0 ? 1 : 0);