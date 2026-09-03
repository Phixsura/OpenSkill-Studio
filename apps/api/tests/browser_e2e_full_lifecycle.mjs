/**
 * Playwright FULL browser E2E — issue #27 §12.4 commercial lifecycle in the UI.
 *
 * Unlike browser_e2e_commercial.mjs (surface render checks), this drives the
 * actual lifecycle through the frontend:
 *   platform console (partner create, tenant ops, credit adjust)
 *   → partner provision wizard (blueprint → name → submit → step polling)
 *   → registry purchase with credit (MarketplacePanel confirm flow)
 *   → tenant billing (invoice list + printable detail) after period close
 *   → platform invoices trace drawer (§37 chain in the UI)
 *   → settlement state machine (generate → finalize → approve → mark paid)
 *   → client portal guest full decision flow (revision → approve → final accept)
 *
 * Backend-only seeding (registration, pack publish, listing, usage, close) goes
 * through the API with the same calls as e2e_commercial_lifecycle.py — the UI
 * has no ops surface for those by design.
 *
 * Usage: node apps/api/tests/browser_e2e_full_lifecycle.mjs
 * Requires: frontend :3000, backend :8000 (APP_ENV=test), Docker infra up.
 * Monitor the API log for 500s while this runs (issue §12.4).
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

// ── API helpers (seeding only) ──
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
// Direct-DB helpers via the API venv (admin promote / outbox drain / period backdate).
// execFileSync + arg array: no shell interpolation of the generated code string.
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
const drainOutbox = () =>
  pyHelper(`
import asyncio
async def go():
    from app.controlplane.worker import process_outbox_once
    from app.core.database import AsyncSessionLocal, engine
    total = 0
    for _ in range(10):
        async with AsyncSessionLocal() as db:
            n = await process_outbox_once(db)
        total += n
        if n == 0:
            break
    await engine.dispose()
    print(total)
asyncio.run(go())`);
const forcePeriodDue = (tenantId) =>
  pyHelper(`
import asyncio
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
async def go():
    from app.controlplane.models.billing import BillingPeriod
    from app.core.database import AsyncSessionLocal, engine
    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(BillingPeriod).where(
            BillingPeriod.tenant_id == "${tenantId}", BillingPeriod.status == "open"
        ))).scalar_one()
        p.period_end = datetime.now(UTC) - timedelta(seconds=1)
        await db.commit()
    await engine.dispose()
    print("ok")
asyncio.run(go())`);

// ── Browser helpers ──
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
  // ═══════════════ SEED (API, mirrors e2e_commercial_lifecycle.py) ═══════════════
  section("0. Seed: admin, partner+rule+blueprint, seller pack+listing");
  const admin = await register("bfl-admin");
  promoteAdmin(admin.email);
  // re-login to refresh role claim in JWT
  const adminLogin = await api("/auth/login", {
    method: "POST",
    body: { email: admin.email, password: "TestPass123!" },
  });
  admin.token = adminLogin.json.access_token;
  check("admin bootstrapped", adminLogin.status === 200);

  // Partner + rev-share rule + partner admin user + blueprint
  const partnerR = await api("/platform/partners", {
    method: "POST",
    token: admin.token,
    body: { name: `BFL Channel ${uid()}`, slug: `bflch-${uid()}`, partner_type: "reseller" },
  });
  check("partner created (API seed)", partnerR.status === 201, partnerR.status);
  const partnerId = partnerR.json.data.id;
  const partnerUser = await register("bfl-partner");
  await api(`/platform/partners/${partnerId}/members`, {
    method: "POST",
    token: admin.token,
    body: { user_id: partnerUser.userId, role: "admin" },
  });
  const ruleR = await api("/platform/revenue-share-rules", {
    method: "POST",
    token: admin.token,
    body: {
      beneficiary_type: "partner",
      partner_id: partnerId,
      revenue_type: "all",
      rule_type: "percentage_of_gross_revenue",
      rate: "10",
      effective_from: "2026-01-01T00:00:00Z",
    },
  });
  await api(`/platform/revenue-share-rules/${ruleR.json.data.id}/activate`, {
    method: "POST",
    token: admin.token,
  });
  const bpR = await api(`/partners/${partnerId}/blueprints`, {
    method: "POST",
    token: partnerUser.token,
    body: {
      name: `BFL blueprint ${uid()}`,
      config: {
        plan_key: "school",
        branding: { product_display_name: "BFL Academy", theme_tokens: { primary: "#123456" } },
        org: { name_template: "{tenant_name} Campus" },
      },
    },
  });
  check("blueprint created (API seed)", bpR.status === 201, JSON.stringify(bpR.json).slice(0, 150));

  // Seller: publishable workflow pack + paid listing (no sell-side UI by design)
  const seller = await register("bfl-seller");
  const sellerOrgR = await api("/orgs", {
    method: "POST",
    token: seller.token,
    body: { name: `BFL Studio ${uid()}` },
  });
  const sellerOrg = sellerOrgR.json.data.id;
  const packR = await api(`/orgs/${sellerOrg}/workflow-packs`, {
    method: "POST",
    token: seller.token,
    body: { name: `BFL Video Suite ${uid()}`, summary: "s", workflow_type: "production" },
  });
  const packId = packR.json.data.id;
  const definition = {
    schema_version: 1,
    inputs: [{ key: "brief", type: "text", required: true }],
    outputs: [{ key: "final", type: "image", from_step: "out", from_port: "delivered" }],
    steps: [
      {
        id: "gen",
        type: "provider_action",
        name: "Generate",
        config: { capability: "image_generation", binding_mode: "auto" },
        inputs: [],
        outputs: [{ port: "result", type: "image" }],
      },
      {
        id: "out",
        type: "output",
        name: "Deliver",
        config: {},
        inputs: [{ port: "final", type: "image" }],
        outputs: [{ port: "delivered", type: "image" }],
      },
    ],
    edges: [{ id: "e1", from_step: "gen", from_port: "result", to_step: "out", to_port: "final" }],
  };
  await api(`/orgs/${sellerOrg}/workflow-packs/${packId}/definition`, {
    method: "PUT",
    token: seller.token,
    body: { definition },
  });
  await api(`/orgs/${sellerOrg}/workflow-packs/${packId}/releases`, {
    method: "POST",
    token: seller.token,
    body: {
      version: "1.0.0",
      changelog: "v1",
      dependencies: { requires_capabilities: [{ capability: "image_generation", features: [] }] },
    },
  });
  await api(`/orgs/${sellerOrg}/workflow-packs/${packId}/submit-review`, {
    method: "POST",
    token: seller.token,
  });
  const pubR = await api(`/orgs/${sellerOrg}/workflow-packs/${packId}/approve`, {
    method: "POST",
    token: seller.token,
  });
  check("pack published (API seed)", pubR.status === 200, pubR.status);
  const sellerTenantR = await api("/tenants/mine", { token: seller.token });
  const sellerTenant = sellerTenantR.json.data[0].id;
  await api(`/platform/tenants/${sellerTenant}/entitlements/paid_marketplace`, {
    method: "PUT",
    token: admin.token,
    body: { value: true, reason: "bfl e2e" },
  });
  const listR = await api(`/orgs/${sellerOrg}/marketplace/listings`, {
    method: "POST",
    token: seller.token,
    body: {
      product_type: "workflow_pack",
      product_id: packId,
      offer_type: "paid",
      price_minor: 21494,
      currency: "USD",
      license_scope: "organization",
    },
  });
  await api(`/orgs/${sellerOrg}/marketplace/listings/${listR.json.data.id}/activate`, {
    method: "POST",
    token: seller.token,
  });
  check("paid listing active (API seed)", listR.status === 201, listR.status);

  // ═══════════════ 1. PARTNER PROVISION WIZARD (UI) ═══════════════
  section("1. Partner provision wizard drives a real provision run");
  const pctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const ppage = await newPage(pctx);
  await uiLogin(ppage, partnerUser.email);
  await ppage.goto(`${BASE}/partner/${partnerId}/provision`, { waitUntil: "networkidle" });
  check("provision wizard renders", (await bodyText(ppage)).includes("Provision a branded tenant"));
  const tenantName = `BFL Education ${uid()}`;
  const tenantSlug = `bfl-edu-${uid()}`;
  await ppage.selectOption("select", { index: 1 }); // first real blueprint
  await ppage.fill('input[placeholder*="Customer name"]', tenantName);
  await ppage.fill('input[placeholder*="Slug"]', tenantSlug);
  await ppage.click('button:has-text("Provision tenant")');
  // Run executes via outbox — drain inline (worker-less) with retries so the
  // page's 2s poll observes completion even if the first drain races the POST.
  for (let i = 0; i < 4; i++) {
    await ppage.waitForTimeout(1500);
    drainOutbox();
    if ((await bodyText(ppage)).includes("Tenant provisioned:")) break;
  }
  await ppage.waitForSelector("text=Tenant provisioned:", { timeout: 20000 });
  const provBody = await bodyText(ppage);
  check("provision run completes in UI (step polling)", provBody.includes("Tenant provisioned:"));
  const tenantIdMatch = provBody.match(/Tenant provisioned:\s*([0-9A-Z]{26})/);
  const tenantId = tenantIdMatch?.[1];
  check("tenant id surfaced in run panel", Boolean(tenantId), provBody.slice(-300));
  await ppage.screenshot({ path: "/tmp/bfl-01-provision-run.png", fullPage: true });

  // Attributed tenant appears on the partner Tenants tab
  await ppage.goto(`${BASE}/partner/${partnerId}/tenants`, { waitUntil: "networkidle" });
  check("attributed tenant listed", (await bodyText(ppage)).includes(tenantSlug));

  // Make the partner admin also the tenant owner (API — platform-only op)
  await api(`/tenants/${tenantId}/members`, {
    method: "POST",
    token: admin.token,
    body: { user_id: partnerUser.userId, role: "owner" },
  });

  // ═══════════════ 2. PLATFORM CONSOLE: tenant detail + credit adjust (UI) ═══════════════
  section("2. Platform console: search, tenant detail, credit adjust");
  const actx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const apage = await newPage(actx);
  await uiLogin(apage, admin.email);
  await apage.goto(`${BASE}/platform`, { waitUntil: "networkidle" });
  check("platform dashboard renders for admin", (await bodyText(apage)).includes("Platform dashboard"));
  await apage.goto(`${BASE}/platform/tenants`, { waitUntil: "networkidle" });
  await apage.fill('input[placeholder*="Search name"]', tenantSlug);
  await apage.waitForTimeout(1200);
  const searchBody = await bodyText(apage);
  check("tenant search finds provisioned tenant", searchBody.includes(tenantSlug));
  await apage.goto(`${BASE}/platform/tenants/${tenantId}`, { waitUntil: "networkidle" });
  const lifecycleOk = await apage
    .waitForSelector("text=Lifecycle", { timeout: 15000 })
    .then(() => true)
    .catch(() => false);
  check("tenant detail renders lifecycle section", lifecycleOk, apage.url());
  // Credit adjust +$500 through the UI (drives POST /platform/tenants/{id}/credits/adjust)
  await apage.fill('input[placeholder^="Amount ("]', "500");
  await apage.fill('input[placeholder="Reason (audited)"]', "bfl e2e top-up");
  await apage.click('button:has-text("Apply")');
  await apage.waitForSelector("text=Credit adjusted", { timeout: 10000 });
  check("credit adjusted via UI (toast)", true);
  await apage.screenshot({ path: "/tmp/bfl-02-tenant-detail.png", fullPage: true });

  // Ledger reflects it on the tenant credits page (partner-owner view)
  await ppage.goto(`${BASE}/dashboard/tenant/${tenantId}/credits`, { waitUntil: "networkidle" });
  const creditBody = await bodyText(ppage);
  check("tenant credits page shows balance", creditBody.includes("Balances"));
  check("ledger shows the $500 adjustment", /500\.00|adjustment/.test(creditBody), creditBody.slice(0, 300));

  // ═══════════════ 3. BUYER PURCHASE VIA MARKETPLACE PANEL (UI) ═══════════════
  section("3. Registry purchase with credit (MarketplacePanel)");
  // The provisioned tenant's org admin = partner user is NOT an org member;
  // find the blueprint-created org and use an invited admin? Simpler: the
  // partner user was added as tenant owner; org membership comes from the
  // provision blueprint (created_by = provision actor = partner user).
  const orgsR = await api("/orgs", { token: partnerUser.token });
  const buyerOrg = orgsR.json.data.find((o) => o.name.includes("Campus"))?.id ?? orgsR.json.data[0]?.id;
  check("buyer org exists (blueprint-created)", Boolean(buyerOrg));
  await ppage.goto(`${BASE}/registry/workflows/${packId}`, { waitUntil: "networkidle" });
  await ppage.waitForTimeout(1500);
  const listingBody = await bodyText(ppage);
  check("price badge renders on registry detail", /214\.94|21494|\$214/.test(listingBody), listingBody.slice(0, 200));
  const purchaseBtn = ppage.locator('button:has-text("Purchase license")');
  check("Purchase license button visible", (await purchaseBtn.count()) > 0);
  await purchaseBtn.first().click();
  // R101[L4/H13]: confirm step now shows the amount + a payment-method select
  await ppage.waitForSelector('button:has-text("Confirm")', { timeout: 5000 });
  await ppage.click('button:has-text("Confirm")');
  await ppage.waitForSelector("text=Purchased — the pack is now licensed", { timeout: 15000 });
  check("purchase succeeds via UI (toast)", true);
  await ppage.waitForTimeout(1000);
  check("licensed badge appears", (await bodyText(ppage)).includes("Licensed"));
  await ppage.screenshot({ path: "/tmp/bfl-03-purchased.png", fullPage: true });

  // License visible on tenant licenses tab
  await ppage.goto(`${BASE}/dashboard/tenant/${tenantId}/licenses`, { waitUntil: "networkidle" });
  const licBody = await bodyText(ppage);
  check("license row on tenant Licenses tab", licBody.includes("purchase"), licBody.slice(0, 300));
  check("purchase row shows amount", /214\.94/.test(licBody), licBody.slice(0, 300));

  // ═══════════════ 4. USAGE → RATING → PERIOD CLOSE → INVOICE (UI verify) ═══════════════
  section("4. Billing: usage rated, period closed, invoice in tenant UI");
  // Tenant sell-price policy so usage rates to a non-zero billable
  // (without it the global cost-plus fallback prices no-rate usage at 0)
  const policyR = await api("/platform/price-policies", {
    method: "POST",
    token: admin.token,
    body: {
      name: `bfl image pricing ${uid()}`,
      policy_type: "fixed_unit_price",
      usage_type: "image_generation",
      tenant_id: tenantId,
      currency: "USD",
      params: { unit_price_minor: 30 },
      effective_from: "2026-01-01T00:00:00Z",
    },
  });
  check("tenant price policy created (API seed)", policyR.status === 201, policyR.status);
  // Manual usage ingestion (API — org admin surface, no UI for ingestion by design)
  const usageR = await api(`/orgs/${buyerOrg}/usage-events`, {
    method: "POST",
    token: partnerUser.token,
    body: {
      usage_type: "image_generation",
      quantity: "40",
      occurred_at: new Date(Date.now() - 60000).toISOString(),
      idempotency_key: `bfl-usage-${uid()}`,
      provider: "mock",
      model_or_service: "mock-image-1",
    },
  });
  check("usage ingested (API seed)", usageR.status === 201, usageR.status);
  drainOutbox(); // rating
  forcePeriodDue(tenantId);
  const closeR = await api("/platform/billing/close-periods", { method: "POST", token: admin.token });
  check("close-periods triggered", closeR.status === 200, closeR.status);
  drainOutbox(); // close handler + accrual

  // Tenant billing page shows the invoice
  await ppage.goto(`${BASE}/dashboard/tenant/${tenantId}/billing`, { waitUntil: "networkidle" });
  await ppage.waitForTimeout(1000);
  const billBody = await bodyText(ppage);
  check("subscription card shows school plan", /school/i.test(billBody), billBody.slice(0, 300));
  const invLink = ppage.locator('a[href*="/billing/invoices/"]').first();
  check("invoice number links to detail", (await invLink.count()) > 0, billBody.slice(0, 400));
  await invLink.click();
  await ppage.waitForSelector("text=Subtotal", { timeout: 10000 });
  const invBody = await bodyText(ppage);
  check("printable invoice renders totals", invBody.includes("Amount due"));
  check("invoice carries plan line", /[Ss]chool/.test(invBody), invBody.slice(0, 400));
  check("invoice carries usage line", /image.generation|image_generation/i.test(invBody), invBody.slice(0, 500));
  check("invoice applies credit", invBody.includes("Credit applied"));
  await ppage.screenshot({ path: "/tmp/bfl-04-invoice.png", fullPage: true });

  // ═══════════════ 5. §37 TRACE DRAWER (UI) ═══════════════
  section("5. Platform invoices: trace drawer reaches provider snapshots");
  await apage.goto(`${BASE}/platform/invoices?tenant_id=${tenantId}`, { waitUntil: "networkidle" });
  await apage.fill('input[placeholder*="tenant ID" i]', tenantId).catch(() => {});
  await apage.waitForTimeout(1500);
  // Invoices render as collapsed <details> — expand them so line buttons are
  // visible. ($$eval is Playwright's page-context DOM helper taking a function
  // literal — not string eval.)
  await apage.$$eval("details", (els) => els.forEach((d) => d.setAttribute("open", "")));
  const traceBtn = apage.locator('button:has-text("Trace")').first();
  check("Trace button on usage line", (await traceBtn.count()) > 0, (await bodyText(apage)).slice(0, 300));
  if ((await traceBtn.count()) > 0) {
    await traceBtn.click();
    await apage.waitForSelector("text=Billing trace", { timeout: 10000 });
    check("trace drawer opens", true);
    // Trace query loads async inside the drawer — wait for the snapshot blocks
    const costSnapOk = await apage
      .waitForSelector("text=Cost rate snapshot", { timeout: 10000 })
      .then(() => true)
      .catch(() => false);
    check("cost rate snapshot present", costSnapOk);
    check("sell rate snapshot present", (await bodyText(apage)).includes("Sell rate snapshot"));
    check("provider call block present", (await bodyText(apage)).includes("Provider call"));
    await apage.screenshot({ path: "/tmp/bfl-05-trace-drawer.png", fullPage: true });
    await apage.click('button:has-text("Close")');
  }

  // ═══════════════ 6. SETTLEMENT STATE MACHINE (UI) ═══════════════
  section("6. Settlements: generate → finalize → approve → mark paid");
  const period = new Date().toISOString().slice(0, 7);
  await apage.goto(`${BASE}/platform/settlements`, { waitUntil: "networkidle" });
  await apage.fill('input[placeholder="Partner ID"]', partnerId);
  await apage.fill('input[placeholder*="Period"]', period);
  await apage.click('button:has-text("Generate")');
  await apage.waitForSelector("text=Statement generated", { timeout: 10000 });
  check("statement generated via UI", true);
  await apage.waitForTimeout(1000);
  await apage.click('button:has-text("Finalize")');
  await apage.waitForSelector("text=Statement updated", { timeout: 10000 });
  check("statement finalized via UI", true);
  await apage.waitForTimeout(1000);
  await apage.click('button:has-text("Approve")');
  await apage.waitForSelector('input[placeholder="Payment ref"]', { timeout: 10000 });
  check("statement approved via UI", true);
  await apage.fill('input[placeholder="Payment ref"]', `wire-${uid()}`);
  await apage.click('button:has-text("Mark paid")');
  await apage.waitForTimeout(1500);
  const setBody = await bodyText(apage);
  check("statement marked paid", setBody.includes("paid_externally") || setBody.includes("paid"), setBody.slice(0, 300));
  await apage.screenshot({ path: "/tmp/bfl-06-settlement.png", fullPage: true });

  // Partner sees the statement + CSV export button
  await ppage.goto(`${BASE}/partner/${partnerId}/statements`, { waitUntil: "networkidle" });
  const stListBody = await bodyText(ppage);
  check("partner statement list shows period", stListBody.includes(period), stListBody.slice(0, 300));
  const stLink = ppage.locator(`a:has-text("${period}")`).first();
  if ((await stLink.count()) > 0) {
    await stLink.click();
    await ppage.waitForSelector("text=Export CSV", { timeout: 10000 });
    const stBody = await bodyText(ppage);
    check("statement detail renders amounts", stBody.includes("Share total"));
    check("share is 10% of gross", /21\.49|2149/.test(stBody), stBody.slice(0, 400));
  } else {
    check("statement detail reachable", false, "period link missing");
  }

  // ═══════════════ 7. CLIENT PORTAL FULL DECISION FLOW (UI) ═══════════════
  section("7. Client portal: guest revision → approve → final accept");
  // Seed: project + submission + share + approver guest link (staff surface)
  const projR = await api(`/orgs/${buyerOrg}/projects`, {
    method: "POST",
    token: partnerUser.token,
    body: {
      title: `BFL Client Video ${uid()}`,
      description: "d",
      instructions: "i",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    },
  });
  check("project created (API seed)", projR.status === 201, projR.status);
  const projectId = projR.json.data.id;
  const subR = await api(`/orgs/${buyerOrg}/projects/${projectId}/submissions`, {
    method: "POST",
    token: partnerUser.token,
  });
  check("submission created (API seed)", subR.status === 201, JSON.stringify(subR.json).slice(0, 150));
  const submissionId = subR.json.data.id;
  const submitR = await api(
    `/orgs/${buyerOrg}/projects/${projectId}/submissions/${submissionId}/submit`,
    { method: "POST", token: partnerUser.token },
  );
  check("submission submitted (API seed)", submitR.status === 200, submitR.status);
  const shareR = await api(`/orgs/${buyerOrg}/projects/${projectId}/client-shares`, {
    method: "POST",
    token: partnerUser.token,
    body: { submission_id: submissionId },
  });
  check("submission shared to portal (API seed)", shareR.status === 201, shareR.status);
  const linkR = await api(`/orgs/${buyerOrg}/projects/${projectId}/client-links`, {
    method: "POST",
    token: partnerUser.token,
    body: {
      label: "BFL Client CEO",
      role: "approver",
      // guest links cap at now+90d — stay inside the window
      expires_at: new Date(Date.now() + 30 * 86400000).toISOString(),
    },
  });
  const guestToken = linkR.json?.data?.token;
  check("guest link minted (API seed)", Boolean(guestToken), JSON.stringify(linkR.json).slice(0, 200));
  if (!guestToken) throw new Error("guest link seeding failed");

  // Guest enters through the access page (fresh context = anonymous)
  const gctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const gpage = await newPage(gctx);
  await gpage.goto(`${BASE}/client/access`, { waitUntil: "networkidle" });
  await gpage.fill('input[placeholder="Access code"]', guestToken);
  await gpage.click('button:has-text("Open project")');
  // /client/access itself matches /client/ — wait for the project URL specifically
  await gpage.waitForURL(new RegExp(`/client/${projectId}`), { timeout: 15000 });
  check("guest session opens project", gpage.url().includes(projectId), gpage.url());
  await gpage.waitForSelector("text=Deliverables", { timeout: 10000 });
  // Submission cards load in a second query after the heading renders
  const versionOk = await gpage
    .waitForSelector("text=Version 1", { timeout: 10000 })
    .then(() => true)
    .catch(() => false);
  check("deliverables render", versionOk, (await bodyText(gpage)).slice(0, 300));

  // Request revision
  await gpage.click('button:has-text("Request revision")');
  await gpage.fill('textarea[placeholder="What should change?"]', "Logo too small on hero frame");
  await gpage.click('button:has-text("Send request")');
  await gpage.waitForSelector("text=Revision requested", { timeout: 10000 });
  check("revision requested via UI", true);
  await gpage.screenshot({ path: "/tmp/bfl-07-revision.png", fullPage: true });

  // Creator resubmits (API — creator dashboard flow out of scope here)
  const resubmitR = await api(
    `/orgs/${buyerOrg}/projects/${projectId}/submissions/${submissionId}/submit`,
    { method: "POST", token: partnerUser.token },
  );
  check("creator resubmits v2 (API seed)", resubmitR.status === 200, JSON.stringify(resubmitR.json).slice(0, 150));

  // Approve + final accept
  await gpage.reload({ waitUntil: "networkidle" });
  await gpage.waitForSelector('button:has-text("Approve version")', { timeout: 10000 });
  await gpage.click('button:has-text("Approve version")');
  await gpage.waitForSelector("text=Version approved", { timeout: 10000 });
  check("version approved via UI", true);
  await gpage.click('button:has-text("Final accept")');
  await gpage.waitForSelector("text=Project finally accepted", { timeout: 10000 });
  check("final accept via UI", true);
  await gpage.reload({ waitUntil: "networkidle" });
  const finalBody = await bodyText(gpage);
  check("acceptance banner persists", finalBody.includes("finally accepted"));
  check("action buttons hidden after acceptance", !finalBody.includes("Request revision"));
  check("decision history renders", finalBody.includes("Decision history"));
  await gpage.screenshot({ path: "/tmp/bfl-08-final-accept.png", fullPage: true });
  await gctx.close();

  // ═══════════════ 8. AUDIT TRAIL VISIBLE IN CONSOLE (UI) ═══════════════
  section("8. Platform audit explorer shows the lifecycle");
  await apage.goto(`${BASE}/platform/audit`, { waitUntil: "networkidle" });
  await apage.fill('input[placeholder="Tenant ID"]', tenantId);
  await apage.waitForTimeout(1500);
  const auditBody = await bodyText(apage);
  check("audit shows tenant.provisioned", auditBody.includes("tenant.provisioned"), auditBody.slice(0, 300));
  check("audit shows credit adjustment", auditBody.includes("credit."), auditBody.slice(0, 300));
  await apage.screenshot({ path: "/tmp/bfl-09-audit.png", fullPage: true });

  await pctx.close();
  await actx.close();

  // ═══════════════ 9. CONSOLE ERRORS ═══════════════
  section("9. Console errors");
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
console.log(`  Screenshots: /tmp/bfl-*.png`);
console.log("=".repeat(60));
process.exit(fail > 0 ? 1 : 0);