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
import { loginInBrowser, registerUser, type AuthContext } from "./helpers";

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
