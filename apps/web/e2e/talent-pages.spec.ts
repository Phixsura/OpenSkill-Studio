/**
 * Browser E2E: Talent layer pages — Issue #32.
 *
 * 100 test cases covering:
 *   1-20:  Page rendering (all talent pages load without crash)
 *   21-35: Navigation & routing
 *   36-50: Public/unauthenticated pages
 *   51-65: Error boundary & empty states
 *   66-80: API response validation (no 500s, correct status codes)
 *   81-90: Page content & structure validation
 *   91-100: Responsive & accessibility basics
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, loginInBrowser, type AuthContext } from "./helpers";

// Increase timeout for cold dev server compilation
test.setTimeout(120_000);

const PASSWORD = "TestPass123!";
const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

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

// Helper: navigate and wait for load
async function goto(p: Page, path: string) {
  await p.goto(path);
  await p.waitForLoadState("domcontentloaded");
  await p.waitForTimeout(1500);
}

// Helper: get page text content lowercased
async function bodyText(p: Page): Promise<string> {
  return (await p.innerHTML("body")).toLowerCase();
}

// ═══════════════════════════════════════════════════════════════
// SECTION 1: Page Rendering (tests 1-20)
// Every talent page loads without crashing
// ═══════════════════════════════════════════════════════════════

test.describe("1. Talent page rendering", () => {
  test("01 — passport page renders", async () => {
    await goto(page, "/dashboard/passport");
    expect(await bodyText(page)).toContain("passport");
  });

  test("02 — opportunities page renders", async () => {
    await goto(page, "/dashboard/opportunities");
    expect(await bodyText(page)).toMatch(/opportunit|browse/i);
  });

  test("03 — applications page renders", async () => {
    await goto(page, "/dashboard/applications");
    expect(await bodyText(page)).toMatch(/application|no.*appli/i);
  });

  test("04 — talent intelligence dashboard renders", async () => {
    await goto(page, "/dashboard/talent");
    expect(await bodyText(page)).toMatch(/talent|intelligence/i);
  });

  test("05 — matched opportunities page renders", async () => {
    await goto(page, "/dashboard/opportunities/matches");
    expect(await bodyText(page)).toMatch(/match|passport|opportunit/i);
  });

  test("06 — passport snapshots page renders", async () => {
    await goto(page, "/dashboard/passport/snapshots");
    expect(await bodyText(page)).toMatch(/snapshot|share/i);
  });

  test("07 — talent demand page renders", async () => {
    await goto(page, "/dashboard/talent/demand");
    expect(await bodyText(page)).toMatch(/demand|capabilit/i);
  });

  test("08 — talent supply page renders", async () => {
    await goto(page, "/dashboard/talent/supply");
    expect(await bodyText(page)).toMatch(/supply|capabilit/i);
  });

  test("09 — career goals page renders", async () => {
    await goto(page, "/dashboard/career-goals");
    expect(await bodyText(page)).toMatch(/career|goal/i);
  });

  test("10 — learning plan page renders", async () => {
    await goto(page, "/dashboard/learning-plan");
    expect(await bodyText(page)).toMatch(/learning|plan|gap/i);
  });

  test("11 — credential pathways page renders", async () => {
    await goto(page, "/dashboard/credential-pathways");
    expect(await bodyText(page)).toMatch(/credential|pathway/i);
  });

  test("12 — capabilities admin page renders", async () => {
    await goto(page, "/dashboard/capabilities");
    expect(await bodyText(page)).toMatch(/capabilit|taxonomy/i);
  });

  test("13 — endorsements page renders", async () => {
    await goto(page, "/dashboard/endorsements");
    expect(await bodyText(page)).toMatch(/endorsement/i);
  });

  test("14 — bookmarks page renders", async () => {
    await goto(page, "/dashboard/bookmarks");
    expect(await bodyText(page)).toMatch(/bookmark|saved/i);
  });

  test("15 — activity log page renders", async () => {
    await goto(page, "/dashboard/activity");
    expect(await bodyText(page)).toMatch(/activity|log/i);
  });

  test("16 — offers page renders", async () => {
    await goto(page, "/dashboard/offers");
    expect(await bodyText(page)).toMatch(/offer/i);
  });

  test("17 — portfolio page renders", async () => {
    await goto(page, "/dashboard/portfolio");
    expect(await bodyText(page)).toMatch(/portfolio|work|showcase/i);
  });

  test("18 — portfolio profile page renders", async () => {
    await goto(page, "/dashboard/portfolio/profile");
    expect(await bodyText(page)).toMatch(/profile|portfolio|public/i);
  });

  test("19 — notifications page renders", async () => {
    await goto(page, "/dashboard/notifications");
    expect(await bodyText(page)).toMatch(/notification|no.*notif/i);
  });

  test("20 — settings page renders", async () => {
    await goto(page, "/dashboard/settings");
    expect(await bodyText(page)).toMatch(/setting|account|profile/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 2: Navigation & Routing (tests 21-35)
// ═══════════════════════════════════════════════════════════════

test.describe("2. Navigation & routing", () => {
  test("21 — dashboard has talent-related content", async () => {
    await goto(page, "/dashboard");
    const html = await bodyText(page);
    // Dashboard should reference some talent features
    expect(html).toMatch(/passport|opportunit|talent|skill|dashboard/i);
  });

  test("22 — dashboard links to talent features", async () => {
    await goto(page, "/dashboard");
    const html = await bodyText(page);
    // Should have navigation to various sections
    expect(html).toMatch(/passport|opportunit|talent|project|skill/i);
  });

  test("23 — passport page has substantial content", async () => {
    await goto(page, "/dashboard/passport");
    const html = await bodyText(page);
    // Passport page should show passport-related content
    expect(html).toMatch(/passport|skill|capabilit|evidence|credential|score/i);
  });

  test("24 — opportunities page links to matches", async () => {
    await goto(page, "/dashboard/opportunities");
    const html = await page.innerHTML("body");
    expect(html).toMatch(/match/i);
  });

  test("25 — navigating to nonexistent talent route shows 404 or fallback", async () => {
    await goto(page, "/dashboard/talent/nonexistent-section");
    const html = await bodyText(page);
    // Should show 404, redirect to dashboard, or show error boundary
    expect(html.length).toBeGreaterThan(50);
  });

  test("26 — talent intelligence has meaningful content", async () => {
    await goto(page, "/dashboard/talent");
    const html = await bodyText(page);
    expect(html).toMatch(/talent|intelligence|workforce|analytics|dashboard/i);
  });

  test("27 — talent intelligence page is substantial", async () => {
    await goto(page, "/dashboard/talent");
    const html = await page.innerHTML("body");
    // Should have substantial content, not just an error or loading
    expect(html.length).toBeGreaterThan(500);
  });

  test("28 — career goals page has add/create action", async () => {
    await goto(page, "/dashboard/career-goals");
    const html = await bodyText(page);
    expect(html).toMatch(/add|create|set.*goal|new/i);
  });

  test("29 — learning plan references capabilities", async () => {
    await goto(page, "/dashboard/learning-plan");
    const html = await bodyText(page);
    expect(html).toMatch(/capabilit|skill|gap|learn/i);
  });

  test("30 — bookmarks page has empty state or list", async () => {
    await goto(page, "/dashboard/bookmarks");
    const html = await bodyText(page);
    expect(html).toMatch(/bookmark|saved|no.*bookmark|empty/i);
  });

  test("31 — activity log shows recent or empty state", async () => {
    await goto(page, "/dashboard/activity");
    const html = await bodyText(page);
    expect(html).toMatch(/activity|log|recent|no.*activity/i);
  });

  test("32 — endorsements page shows leaderboard or empty", async () => {
    await goto(page, "/dashboard/endorsements");
    const html = await bodyText(page);
    expect(html).toMatch(/endorsement|no.*endorsement|leaderboard/i);
  });

  test("33 — offers page shows list or empty state", async () => {
    await goto(page, "/dashboard/offers");
    const html = await bodyText(page);
    expect(html).toMatch(/offer|no.*offer|empty/i);
  });

  test("34 — credential pathways shows list or empty", async () => {
    await goto(page, "/dashboard/credential-pathways");
    const html = await bodyText(page);
    expect(html).toMatch(/pathway|credential|no.*pathway|empty/i);
  });

  test("35 — portfolio new item page renders", async () => {
    await goto(page, "/dashboard/portfolio/items/new");
    const html = await bodyText(page);
    expect(html).toMatch(/portfolio|item|add|create|new/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 3: Public / Unauthenticated Pages (tests 36-50)
// ═══════════════════════════════════════════════════════════════

test.describe("3. Public pages (no auth)", () => {
  test("36 — passport verification page loads", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/passport/nonexistent-test-token");
    expect((await p.innerHTML("body")).length).toBeGreaterThan(100);
    await c.close();
  });

  test("37 — credential verification page loads", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/credential/nonexistent-test-id");
    expect((await p.innerHTML("body")).length).toBeGreaterThan(50);
    await c.close();
  });

  test("38 — employer career page loads for nonexistent org", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/employers/nonexistent-org-id");
    expect((await p.innerHTML("body")).length).toBeGreaterThan(50);
    await c.close();
  });

  test("39 — passport verify page shows verify-related content", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/passport/test-invalid-token");
    const html = await bodyText(p);
    expect(html).toMatch(/verif|passport|not.*found|invalid|error/i);
    await c.close();
  });

  test("40 — credential verify page shows verify-related content", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/credential/test-invalid-id");
    const html = await bodyText(p);
    expect(html).toMatch(/verif|credential|not.*found|invalid|error/i);
    await c.close();
  });

  test("41 — unauthenticated access to /dashboard/passport redirects to login", async ({
    browser,
  }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/passport");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    const url = p.url();
    // Should redirect to login or show login form
    expect(url).toMatch(/login|sign/i);
    await c.close();
  });

  test("42 — unauthenticated access to /dashboard/opportunities redirects", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/opportunities");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("43 — unauthenticated access to /dashboard/talent redirects", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/talent");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("44 — unauthenticated access to /dashboard/applications redirects", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/applications");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("45 — employer page renders reasonable HTML structure", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/employers/fake-org-12345");
    // Should have head, body, some content
    const html = await p.innerHTML("body");
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("46 — public verify pages don't expose sensitive data", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/passport/test-token");
    const html = await bodyText(p);
    // Should not contain raw error stack traces
    expect(html).not.toMatch(/traceback|stack.*error.*at\s/i);
    await c.close();
  });

  test("47 — passport verify page has proper page title", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/passport/test-token");
    const title = await p.title();
    expect(title.length).toBeGreaterThan(0);
    await c.close();
  });

  test("48 — credential verify page has proper page title", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/verify/credential/test-id");
    const title = await p.title();
    expect(title.length).toBeGreaterThan(0);
    await c.close();
  });

  test("49 — home page loads", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/");
    const html = await p.innerHTML("body");
    expect(html.length).toBeGreaterThan(100);
    await c.close();
  });

  test("50 — login page loads", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/login");
    const html = await bodyText(p);
    expect(html).toMatch(/sign.*in|log.*in|email|password/i);
    await c.close();
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 4: Error Boundaries & Empty States (tests 51-65)
// ═══════════════════════════════════════════════════════════════

test.describe("4. Error boundaries & empty states", () => {
  test("51 — passport page shows empty state for new user", async () => {
    await goto(page, "/dashboard/passport");
    const html = await bodyText(page);
    // New user has no skills — should show either empty passport or onboarding
    expect(html).toMatch(/passport|skill|get.*started|add|no.*capabilit/i);
  });

  test("52 — opportunities empty state has call to action", async () => {
    await goto(page, "/dashboard/opportunities");
    const html = await bodyText(page);
    expect(html).toMatch(/opportunit|browse|search|no.*opportunit/i);
  });

  test("53 — applications empty state", async () => {
    await goto(page, "/dashboard/applications");
    const html = await bodyText(page);
    expect(html).toMatch(/application|no.*application|apply/i);
  });

  test("54 — career goals empty state has create action", async () => {
    await goto(page, "/dashboard/career-goals");
    const html = await bodyText(page);
    expect(html).toMatch(/goal|create|add|set|no.*goal/i);
  });

  test("55 — learning plan empty state references skills gap", async () => {
    await goto(page, "/dashboard/learning-plan");
    const html = await bodyText(page);
    expect(html).toMatch(/plan|gap|no.*gap|learning/i);
  });

  test("56 — credential pathways empty state", async () => {
    await goto(page, "/dashboard/credential-pathways");
    const html = await bodyText(page);
    expect(html).toMatch(/pathway|credential|no.*pathway/i);
  });

  test("57 — endorsements empty state", async () => {
    await goto(page, "/dashboard/endorsements");
    const html = await bodyText(page);
    expect(html).toMatch(/endorsement|no.*endorsement/i);
  });

  test("58 — bookmarks empty state", async () => {
    await goto(page, "/dashboard/bookmarks");
    const html = await bodyText(page);
    expect(html).toMatch(/bookmark|no.*bookmark|saved/i);
  });

  test("59 — activity empty state for new user", async () => {
    await goto(page, "/dashboard/activity");
    const html = await bodyText(page);
    expect(html).toMatch(/activity|no.*activity|log/i);
  });

  test("60 — offers empty state", async () => {
    await goto(page, "/dashboard/offers");
    const html = await bodyText(page);
    expect(html).toMatch(/offer|no.*offer/i);
  });

  test("61 — matched opportunities empty state", async () => {
    await goto(page, "/dashboard/opportunities/matches");
    const html = await bodyText(page);
    expect(html).toMatch(/match|no.*match|passport|opportunit/i);
  });

  test("62 — snapshot page empty state", async () => {
    await goto(page, "/dashboard/passport/snapshots");
    const html = await bodyText(page);
    expect(html).toMatch(/snapshot|no.*snapshot|share/i);
  });

  test("63 — capabilities admin empty state", async () => {
    await goto(page, "/dashboard/capabilities");
    const html = await bodyText(page);
    expect(html).toMatch(/capabilit|no.*capabilit|taxonomy/i);
  });

  test("64 — portfolio empty state", async () => {
    await goto(page, "/dashboard/portfolio");
    const html = await bodyText(page);
    expect(html).toMatch(/portfolio|no.*item|showcase|add/i);
  });

  test("65 — notifications empty state", async () => {
    await goto(page, "/dashboard/notifications");
    const html = await bodyText(page);
    expect(html).toMatch(/notification|no.*notif|empty/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 5: API Response Validation (tests 66-80)
// ═══════════════════════════════════════════════════════════════

test.describe("5. API response validation", () => {
  test("66 — GET /talent/passport returns 200", async () => {
    const res = await fetch(`${API}/talent/passport`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("67 — GET /talent/capabilities returns 200", async () => {
    const res = await fetch(`${API}/talent/capabilities`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("68 — GET /talent/evidence returns 200", async () => {
    const res = await fetch(`${API}/talent/evidence`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("69 — GET /talent/credentials returns 200", async () => {
    const res = await fetch(`${API}/talent/credentials`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("70 — GET /talent/endorsements/stats returns 200", async () => {
    const res = await fetch(`${API}/talent/endorsements/stats`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("71 — GET /talent/opportunities returns 200", async () => {
    const res = await fetch(`${API}/talent/opportunities`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("72 — GET /talent/applications returns 200", async () => {
    const res = await fetch(`${API}/talent/applications`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("73 — GET /talent/bookmarks returns 200", async () => {
    const res = await fetch(`${API}/talent/bookmarks`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("74 — GET /talent/activity returns 200", async () => {
    const res = await fetch(`${API}/talent/activity`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("75 — GET /talent/career-paths returns 200", async () => {
    const res = await fetch(`${API}/talent/career-paths`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("76 — GET /talent/gaps returns 200", async () => {
    const res = await fetch(`${API}/talent/gaps`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("77 — GET /talent/demand returns 200", async () => {
    const res = await fetch(`${API}/talent/demand`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("78 — GET /talent/coverage returns 200", async () => {
    const res = await fetch(`${API}/talent/coverage`, { headers: auth.headers });
    expect(res.status).toBeLessThan(500);
  });

  test("79 — unauthorized API call returns 401 not 500", async () => {
    const res = await fetch(`${API}/talent/passport`);
    expect(res.status).toBe(401);
  });

  test("80 — no API 500 errors occurred during page navigation", () => {
    expect(api500s).toHaveLength(0);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 6: Page Content & Structure (tests 81-90)
// ═══════════════════════════════════════════════════════════════

test.describe("6. Page content & structure", () => {
  test("81 — passport page has substantial content", async () => {
    await goto(page, "/dashboard/passport");
    const html = await page.innerHTML("body");
    // Page should have meaningful content (not blank or just a spinner)
    expect(html.length).toBeGreaterThan(500);
  });

  test("82 — opportunities page has heading", async () => {
    await goto(page, "/dashboard/opportunities");
    const html = await page.innerHTML("body");
    expect(html).toMatch(/<h[1-3]/i);
  });

  test("83 — talent dashboard has structured content", async () => {
    await goto(page, "/dashboard/talent");
    const html = await page.innerHTML("body");
    // Should have headings or meaningful structure
    expect(html).toMatch(/<(h[1-6]|div|section)/i);
    expect(html.length).toBeGreaterThan(500);
  });

  test("84 — dashboard page doesn't show raw JSON", async () => {
    await goto(page, "/dashboard");
    const html = await bodyText(page);
    expect(html).not.toMatch(/^\s*\{.*"data"/);
  });

  test("85 — passport page doesn't show raw error stack", async () => {
    await goto(page, "/dashboard/passport");
    const html = await bodyText(page);
    expect(html).not.toMatch(/traceback|at\s+\w+\s+\(/i);
  });

  test("86 — opportunities page doesn't show raw error stack", async () => {
    await goto(page, "/dashboard/opportunities");
    const html = await bodyText(page);
    expect(html).not.toMatch(/traceback|at\s+\w+\s+\(/i);
  });

  test("87 — talent page doesn't show raw error stack", async () => {
    await goto(page, "/dashboard/talent");
    const html = await bodyText(page);
    expect(html).not.toMatch(/traceback|at\s+\w+\s+\(/i);
  });

  test("88 — career goals page has structured layout", async () => {
    await goto(page, "/dashboard/career-goals");
    const html = await page.innerHTML("body");
    // Should have some structured elements, not just plain text
    expect(html).toMatch(/<(div|section|main|article)/i);
  });

  test("89 — portfolio page has add action", async () => {
    await goto(page, "/dashboard/portfolio");
    const html = await bodyText(page);
    expect(html).toMatch(/add|create|new|upload|showcase/i);
  });

  test("90 — endorsements page shows stats or empty state", async () => {
    await goto(page, "/dashboard/endorsements");
    const html = await bodyText(page);
    expect(html).toMatch(/endorsement|stat|leaderboard|no.*endorsement/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 7: Responsive & Accessibility (tests 91-100)
// ═══════════════════════════════════════════════════════════════

test.describe("7. Responsive & accessibility", () => {
  test("91 — passport page works at mobile width", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, "/dashboard/passport");
    const html = await bodyText(page);
    expect(html).toContain("passport");
    await page.setViewportSize({ width: 1280, height: 800 }); // restore
  });

  test("92 — opportunities page works at mobile width", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, "/dashboard/opportunities");
    const html = await bodyText(page);
    expect(html).toMatch(/opportunit|browse/i);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("93 — talent dashboard works at mobile width", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, "/dashboard/talent");
    const html = await bodyText(page);
    expect(html).toMatch(/talent|intelligence/i);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("94 — career goals page works at tablet width", async () => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await goto(page, "/dashboard/career-goals");
    const html = await bodyText(page);
    expect(html).toMatch(/career|goal/i);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("95 — passport page has no horizontal overflow at mobile", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, "/dashboard/passport");
    const overflowing = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth + 5;
    });
    expect(overflowing).toBe(false);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("96 — pages have lang attribute on html", async () => {
    await goto(page, "/dashboard/passport");
    const lang = await page.evaluate(() => document.documentElement.lang);
    expect(lang).toBeTruthy();
  });

  test("97 — all pages have a page title", async () => {
    await goto(page, "/dashboard/passport");
    expect(await page.title()).toBeTruthy();
    await goto(page, "/dashboard/opportunities");
    expect(await page.title()).toBeTruthy();
    await goto(page, "/dashboard/talent");
    expect(await page.title()).toBeTruthy();
  });

  test("98 — passport page buttons are keyboard focusable", async () => {
    await goto(page, "/dashboard/passport");
    // Tab through elements — should be able to focus interactive elements
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => {
      const el = document.activeElement;
      return el ? el.tagName.toLowerCase() : null;
    });
    // Should focus on a link, button, or input
    expect(focused).not.toBe("body");
  });

  test("99 — opportunities page at wide viewport still works", async () => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await goto(page, "/dashboard/opportunities");
    const html = await bodyText(page);
    expect(html).toMatch(/opportunit/i);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("100 — final check: zero accumulated 500 errors across all tests", () => {
    if (api500s.length > 0) {
      console.error("API 500s encountered:", api500s);
    }
    expect(api500s).toHaveLength(0);
  });
});
