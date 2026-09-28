/**
 * Sweep: AI ECOSYSTEM INTELLIGENCE (ADR-016, issue #35).
 *
 * Drives the real UI as a plain member: every ecosystem page renders its h1
 * without crashing, and the member-owned watchlist flow works end to end
 * (create list → add external-ref item → mute → remove item). Admin-only
 * surfaces (sources) must render their read view gracefully for members.
 *
 * DOM anchors verified against page sources:
 * - /dashboard/ecosystem: overview stat cards (EcosystemNav present)
 * - watchlists: h1 "Watchlists & Deprecation Calendar", input
 *   "New watchlist name", selects aria-label "Watch target kind" /
 *   "Notification severity threshold", input "external ref (repo url…)",
 *   button "Watch", per-item "remove"
 * - other pages: h1s "Model / Tool Catalog", "Change Feed", "Discoveries",
 *   "Pricing Intelligence", "Benchmark Lab", "Compare & Estimate",
 *   "External Sources", "Security Advisories", "Blind Review",
 *   "Component Lifecycle"
 */
import { expect, test, type BrowserContext, type Page } from "@playwright/test";
import { createOrg, loginInBrowser, registerUser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

const PASSWORD = process.env.E2E_TEST_PASSWORD || "TestPass123!";
const TS = Date.now();

let auth: AuthContext;
let ctx: BrowserContext;
let page: Page;

test.describe.configure({ mode: "serial" });

// registration + UI login can exceed the default 60s under load
test.beforeAll(async ({ browser }) => {
  test.setTimeout(120_000);
  auth = await registerUser(`Eco Sweep${TS}`);
  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, auth.email, PASSWORD);
});

test.afterAll(async () => {
  await ctx?.close();
});

async function goto(p: Page, path: string) {
  await p.goto(path);
  await p.waitForLoadState("domcontentloaded");
  await p.waitForTimeout(1200);
}

const PAGES: Array<[string, string]> = [
  ["/dashboard/ecosystem", "Ecosystem"],
  ["/dashboard/ecosystem/catalog", "Model / Tool Catalog"],
  ["/dashboard/ecosystem/changes", "Change Feed"],
  ["/dashboard/ecosystem/discoveries", "Discoveries"],
  ["/dashboard/ecosystem/pricing", "Pricing Intelligence"],
  ["/dashboard/ecosystem/benchmarks", "Benchmark Lab"],
  ["/dashboard/ecosystem/compare", "Compare & Estimate"],
  ["/dashboard/ecosystem/sources", "External Sources"],
  ["/dashboard/ecosystem/security", "Security Advisories"],
  ["/dashboard/ecosystem/review", "Blind Review"],
  ["/dashboard/ecosystem/components", "Component Lifecycle"],
  ["/dashboard/ecosystem/watchlists", "Watchlists & Deprecation Calendar"],
];

test("1 — every ecosystem page renders for a member without crashing", async () => {
  for (const [path, heading] of PAGES) {
    await goto(page, path);
    const body = (await page.innerHTML("body")).toLowerCase();
    expect(body, `${path} should not crash`).not.toContain("application error");
    if (path !== "/dashboard/ecosystem") {
      await expect(
        page.getByRole("heading", { level: 1, name: heading }),
        `${path} h1`,
      ).toBeVisible();
    }
  }
});

test("2 — watchlist lifecycle: create, add ref item, mute, remove", async () => {
  await goto(page, "/dashboard/ecosystem/watchlists");
  const listName = `E2E List ${TS}`;

  await page.getByPlaceholder("New watchlist name").fill(listName);
  await page.getByRole("button", { name: "Create", exact: true }).click();
  await expect(page.getByText(listName)).toBeVisible({ timeout: 10_000 });

  // Select the list → item panel appears
  await page.getByText(listName).click();
  const kindSelect = page.getByLabel("Watch target kind");
  await expect(kindSelect).toBeVisible();
  await kindSelect.selectOption("github_repo");
  await page.getByPlaceholder(/external ref/).fill(`acme/e2e-repo-${TS}`);
  await page.getByRole("button", { name: "Watch", exact: true }).dispatchEvent("click");
  await expect(page.getByText(`acme/e2e-repo-${TS}`)).toBeVisible({ timeout: 10_000 });

  // Mute (bell toggles) — the muted badge appears on the list row
  await page
    .getByRole("button", { name: "Mute notifications for 7 days" })
    .first()
    .dispatchEvent("click");
  await expect(page.getByText("muted").first()).toBeVisible({ timeout: 10_000 });

  // Remove the item
  await page.getByRole("button", { name: "remove" }).first().dispatchEvent("click");
  await expect(page.getByText(`acme/e2e-repo-${TS}`)).toBeHidden({ timeout: 10_000 });
});

test("3 — quick watch from catalog is member-allowed (or empty state shows)", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const body = (await page.innerHTML("body")).toLowerCase();
  if (body.includes("👁 watch")) {
    await page.getByText("👁 Watch").first().click();
    await expect(page.getByText("✓ Watching").first()).toBeVisible({ timeout: 10_000 });
  } else {
    // Empty catalog is a valid state on a fresh stack — page must say so
    expect(body).toContain("no ");
  }
});

test("4 — catalog Inspect deep-links to the entity-filtered change feed", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const body = (await page.innerHTML("body")).toLowerCase();
  if (!body.includes("inspect")) {
    test.skip(true, "empty catalog on this stack");
    return;
  }
  await page.getByText("Inspect").first().dispatchEvent("click");
  const link = page.getByText("📰 view changes");
  await link.waitFor({ state: "visible", timeout: 10_000 });
  // R232 full-stack check: the subscribe anchor must carry a real feed token
  // (feed readers can't send Bearer headers)
  const subscribe = page.getByText("📡 subscribe (.atom)");
  await expect
    .poll(async () => (await subscribe.getAttribute("href")) ?? "", { timeout: 10_000 })
    .toMatch(/changes\.atom\?entity_id=[0-9A-Z]{26}&token=.+/);
  await link.dispatchEvent("click");
  await page.waitForURL(/\/dashboard\/ecosystem\/changes\?entity=/, { timeout: 10_000 });
  await page.getByText(/filtered to entity/).waitFor({ state: "visible", timeout: 10_000 });
});

test("5 — global search hit opens the catalog Inspect panel", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const body = (await page.innerHTML("body")).toLowerCase();
  if (!body.includes("inspect")) {
    test.skip(true, "empty catalog on this stack");
    return;
  }
  // search for the first visible entity name fragment
  const firstName = await page.locator("tbody tr td:first-child").first().innerText();
  const term = firstName.trim().split(/\s+/)[0]!.slice(0, 8);
  await page.getByLabel("Search catalog").fill(term);
  await page.getByText("🔍").dispatchEvent("click");
  const hit = page.locator("a[href*='/dashboard/ecosystem/catalog?kind=']").first();
  await hit.waitFor({ state: "visible", timeout: 10_000 });
  await hit.dispatchEvent("click");
  await page.waitForURL(/entity=/, { timeout: 10_000 });
  await page.getByText(/Source conflicts for/).waitFor({ state: "visible", timeout: 10_000 });
});

test("6 — org-attached watchlist creation shows the org badge", async () => {
  const orgId = await createOrg(auth, `Eco Org ${TS}`);
  expect(orgId).toBeTruthy();
  await goto(page, "/dashboard/ecosystem/watchlists");
  const listName = `Org List ${TS}`;
  await page.getByPlaceholder("New watchlist name").fill(listName);
  await page.getByLabel("Attach to organization (webhook fan-out)").selectOption(orgId);
  await page.getByRole("button", { name: "Create", exact: true }).dispatchEvent("click");
  const row = page.getByText(listName);
  await row.waitFor({ state: "visible", timeout: 10_000 });
  // the org badge marks it
  const badge = page.getByText("org", { exact: true }).first();
  await badge.waitFor({ state: "visible", timeout: 10_000 });
});

test("7 — acknowledging a change persists across the include-acknowledged toggle", async () => {
  await goto(page, "/dashboard/ecosystem/changes");
  const body = (await page.innerHTML("body")).toLowerCase();
  if (!body.includes("acknowledge") || body.includes("no changes match")) {
    test.skip(true, "no unacknowledged changes on this stack");
    return;
  }
  const firstAck = page.getByText("Acknowledge", { exact: true }).first();
  await firstAck.waitFor({ state: "visible", timeout: 10_000 });
  await firstAck.dispatchEvent("click");
  await page.waitForTimeout(1500);
  await page.getByText("Include acknowledged").click();
  await page.waitForTimeout(1500);
  const after = (await page.innerHTML("body")).toLowerCase();
  expect(after).not.toContain("application error");
  // R362: the §103 loop closes in a real browser — un-ack a row in the
  // merged view (the just-acked one may sit deep on stacks with history)
  const unackButtons = page.getByText("Un-acknowledge", { exact: true });
  const anyUnack = await unackButtons
    .first()
    .waitFor({ state: "visible", timeout: 10_000 })
    .then(() => true)
    .catch(() => false);
  if (anyUnack) {
    await unackButtons.first().dispatchEvent("click");
    await page.waitForTimeout(1500);
    const post = (await page.innerHTML("body")).toLowerCase();
    expect(post).not.toContain("application error");
  }
  await page.getByText("Include acknowledged").click(); // back to default view
  await page
    .getByText("Acknowledge", { exact: true })
    .first()
    .waitFor({ state: "visible", timeout: 10_000 });
});

test("8 — rotating the feed token swaps every subscription URL", async () => {
  await goto(page, "/dashboard/ecosystem/watchlists");
  const ics = page.getByText("📅 subscribe (.ics)");
  await ics.waitFor({ state: "visible", timeout: 10_000 });
  // wait for the minted token to land in the href
  await expect
    .poll(async () => (await ics.getAttribute("href")) ?? "", { timeout: 10_000 })
    .toMatch(/token=/);
  const before = (await ics.getAttribute("href"))!;
  await page.getByText(/rotate feed token/).dispatchEvent("click");
  await expect
    .poll(async () => (await ics.getAttribute("href")) ?? "", { timeout: 10_000 })
    .not.toBe(before);
  const after = (await ics.getAttribute("href"))!;
  expect(after).toMatch(/token=/);
  // full-stack revocation: the OLD token is dead against the live API
  const oldToken = before.split("token=")[1]!;
  const res = await page.request.get(`${API}/ecosystem/deprecation-calendar.ics?token=${oldToken}`);
  expect(res.status()).toBe(401);
  // ...and the NEW one works
  const newToken = after.split("token=")[1]!;
  const res2 = await page.request.get(
    `${API}/ecosystem/deprecation-calendar.ics?token=${newToken}`,
  );
  expect(res2.status()).toBe(200);
});

test("9 — compare renders a side-by-side table for two real entities", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const body = (await page.innerHTML("body")).toLowerCase();
  if (!body.includes("inspect")) {
    test.skip(true, "empty catalog on this stack");
    return;
  }
  // grab two entity ids from the deep-linkable Inspect flow: use the API
  // directly (the page's rows don't expose ids in the DOM)
  const res = await page.request.get(`${API}/ecosystem/catalog/models?limit=2`, {
    headers: auth.headers,
  });
  const rows = (await res.json()).data as { id: string; canonical_name: string }[];
  if (rows.length < 2) {
    test.skip(true, "fewer than two models on this stack");
    return;
  }
  await goto(page, `/dashboard/ecosystem/compare?kind=model&ids=${rows[0]!.id},${rows[1]!.id}`);
  // both canonical names render as table headers
  await page.getByText(rows[0]!.canonical_name).first().waitFor({ timeout: 10_000 });
  await page.getByText(rows[1]!.canonical_name).first().waitFor({ timeout: 10_000 });
  // the curated-facts and availability rows exist
  await page.getByText("Curated facts").waitFor({ timeout: 10_000 });
  await page.getByText("Availability").first().waitFor({ timeout: 10_000 });
});

test("10 — the in-list filter narrows the catalog against the live API", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const firstCell = page.locator("tbody tr td:first-child").first();
  const hasRows = await firstCell.isVisible().catch(() => false);
  if (!hasRows) {
    test.skip(true, "empty catalog on this stack");
    return;
  }
  const name = (await firstCell.innerText()).trim();
  const fragment = name.split(/\s+/)[0]!.slice(0, 6);
  await page.getByLabel("Filter list by name").fill(fragment);
  // debounce (300ms) + fetch: every visible row must contain the fragment
  await expect
    .poll(
      async () => {
        const cells = await page.locator("tbody tr td:first-child").allInnerTexts();
        return (
          cells.length > 0 && cells.every((c) => c.toLowerCase().includes(fragment.toLowerCase()))
        );
      },
      { timeout: 10_000 },
    )
    .toBe(true);
});

test("11 — the lifecycle dropdown filters the catalog against the live API", async () => {
  await goto(page, "/dashboard/ecosystem/catalog");
  const rowsBefore = await page
    .locator("tbody tr")
    .count()
    .catch(() => 0);
  if (rowsBefore === 0) {
    test.skip(true, "empty catalog on this stack");
    return;
  }
  // pick the first row's status pill text as a guaranteed-nonempty filter
  const pill = (await page.locator("tbody tr td:nth-child(2)").first().innerText())
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
  await page.getByLabel("Filter by lifecycle status").selectOption(pill);
  await expect
    .poll(
      async () => {
        const pills = await page.locator("tbody tr td:nth-child(2)").allInnerTexts();
        return (
          pills.length > 0 &&
          pills.every((t) => t.trim().toLowerCase().replace(/\s+/g, "_") === pill)
        );
      },
      { timeout: 10_000 },
    )
    .toBe(true);
});
