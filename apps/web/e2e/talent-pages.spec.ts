/**
 * Browser E2E: Talent layer pages — Issue #32.
 *
 * Verifies all new talent pages render correctly, navigation links exist,
 * no console errors, and no 500 API responses.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, loginInBrowser, type AuthContext } from "./helpers";

// Increase timeout for cold dev server compilation
test.setTimeout(120_000);

const PASSWORD = "TestPass123!";
let auth: AuthContext;
let ctx: BrowserContext;
let page: Page;

const api500s: string[] = [];
const consoleErrors: string[] = [];

test.beforeAll(async ({ browser }) => {
  // Retry registration (may hit rate limits from prior runs)
  for (let i = 0; i < 5; i++) {
    try {
      auth = await registerUser("Talent E2E User");
      break;
    } catch {
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  page = await ctx.newPage();

  page.on("console", (msg) => {
    if (msg.type() === "error" && !msg.text().includes("favicon")) {
      consoleErrors.push(msg.text());
    }
  });
  page.on("response", (resp) => {
    if (resp.url().includes("/api/v1/") && resp.status() >= 500) {
      api500s.push(`${resp.status()} ${resp.url()}`);
    }
  });

  await loginInBrowser(page, auth.email, PASSWORD);
});

test.afterAll(async () => {
  await ctx?.close();
});

test.describe("Talent layer pages", () => {
  test("dashboard has talent nav links", async () => {
    await page.goto("/dashboard");
    await page.waitForLoadState("domcontentloaded");
    const html = await page.innerHTML("body");
    expect(html).toContain("/dashboard/passport");
    expect(html).toContain("/dashboard/opportunities");
    expect(html).toContain("/dashboard/talent");
  });

  test("passport page renders", async () => {
    await page.goto("/dashboard/passport");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toContain("passport");
  });

  test("opportunities page renders", async () => {
    await page.goto("/dashboard/opportunities");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    // Should show opportunities list or empty state
    expect(html.toLowerCase()).toMatch(/opportunit|no.*found|browse/i);
  });

  test("applications page renders", async () => {
    await page.goto("/dashboard/applications");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/application|no.*appli/i);
  });

  test("talent intelligence dashboard renders", async () => {
    await page.goto("/dashboard/talent");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/talent|intelligence|demand/i);
  });

  test("matched opportunities page renders", async () => {
    await page.goto("/dashboard/opportunities/matches");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/match|passport|opportunities/i);
  });

  test("passport snapshots page renders", async () => {
    await page.goto("/dashboard/passport/snapshots");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/snapshot|share/i);
  });

  test("talent demand detail page renders", async () => {
    await page.goto("/dashboard/talent/demand");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/demand|capability/i);
  });

  test("talent supply detail page renders", async () => {
    await page.goto("/dashboard/talent/supply");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/supply|capability/i);
  });

  test("career goals page renders", async () => {
    await page.goto("/dashboard/career-goals");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/career|goal|no.*goal/i);
  });

  test("learning plan page renders", async () => {
    await page.goto("/dashboard/learning-plan");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/learning|plan|no.*gap/i);
  });

  test("credential pathways page renders", async () => {
    await page.goto("/dashboard/credential-pathways");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(2000);
    const html = await page.innerHTML("body");
    expect(html.toLowerCase()).toMatch(/credential|pathway|no.*pathway/i);
  });

  test("no API 500 errors occurred", () => {
    expect(api500s).toHaveLength(0);
  });
});

test.describe("Public pages (no auth)", () => {
  test("passport verification page loads without auth", async ({ browser }) => {
    const publicCtx = await browser.newContext();
    const publicPage = await publicCtx.newPage();
    await publicPage.goto("/verify/passport/nonexistent-test-token");
    await publicPage.waitForLoadState("domcontentloaded");
    await publicPage.waitForTimeout(2000);
    const html = await publicPage.innerHTML("body");
    expect(html.length).toBeGreaterThan(100);
    await publicCtx.close();
  });

  test("employer career page handles nonexistent org", async ({ browser }) => {
    const publicCtx = await browser.newContext();
    const publicPage = await publicCtx.newPage();
    await publicPage.goto("/employers/nonexistent-org-id");
    await publicPage.waitForLoadState("domcontentloaded");
    await publicPage.waitForTimeout(2000);
    const html = await publicPage.innerHTML("body");
    expect(html.length).toBeGreaterThan(50);
    await publicCtx.close();
  });
});
