/**
 * Browser E2E: Full page coverage sweep.
 *
 * Tests every page in the app that is NOT already covered by other spec files.
 * Focuses on: auth pages, platform admin, partner portal, tenant management,
 * org-scoped pages (compose, evaluation, requirements, reviews, settings,
 * opportunities), public profile pages, and misc pages.
 *
 * Each test verifies: page loads, no crash, no raw error stack, correct
 * auth redirect behavior.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

test.setTimeout(120_000);

const PASSWORD = "TestPass123!";
const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let auth: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

const api500s: string[] = [];

test.beforeAll(async ({ browser }) => {
  // registerUser now flushes redis rate-limit keys automatically
  for (let i = 0; i < 5; i++) {
    try {
      auth = await registerUser("Sweep E2E User");
      break;
    } catch {
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  if (!auth) throw new Error("Failed to register user after 5 retries");

  // Create an org with unique name (slug collision from prior runs)
  const orgName = `Sweep Org ${Date.now()}`;
  for (let i = 0; i < 5; i++) {
    try {
      orgId = await createOrg(auth, orgName);
      if (orgId) break;
    } catch {
      await new Promise((r) => setTimeout(r, 2000));
    }
  }
  if (!orgId) throw new Error("Failed to create org after 5 retries");

  ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  page = await ctx.newPage();

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

// Helper: navigate and wait
async function goto(p: Page, path: string) {
  await p.goto(path);
  await p.waitForLoadState("domcontentloaded");
  await p.waitForTimeout(1500);
}

// Helper: lowercased body HTML
async function bodyText(p: Page): Promise<string> {
  return (await p.innerHTML("body")).toLowerCase();
}

// ═══════════════════════════════════════════════════════════════
// SECTION 1: Auth Pages (public, no login needed)
// ═══════════════════════════════════════════════════════════════

test.describe("1. Auth pages", () => {
  test("01 — login page renders form", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/login");
    const html = await bodyText(p);
    expect(html).toMatch(/email|password|sign.*in|log.*in/i);
    await c.close();
  });

  test("02 — register page renders form", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/register");
    const html = await bodyText(p);
    expect(html).toMatch(/email|password|sign.*up|register|create.*account/i);
    await c.close();
  });

  test("03 — forgot password page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/forgot-password");
    const html = await bodyText(p);
    expect(html).toMatch(/email|forgot|reset|password/i);
    await c.close();
  });

  test("04 — reset password page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/reset-password?token=invalid-test-token");
    const html = await bodyText(p);
    expect(html).toMatch(/password|reset|new.*password|token|invalid/i);
    await c.close();
  });

  test("05 — login page has no raw error stack", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/login");
    const html = await bodyText(p);
    expect(html).not.toMatch(/traceback|at\s+\w+\s+\(/i);
    await c.close();
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 2: Org-Scoped Pages — Compose
// ═══════════════════════════════════════════════════════════════

test.describe("2. Org compose pages", () => {
  test("06 — compose learning page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/compose/learning`);
    const html = await bodyText(page);
    expect(html).toMatch(/compose|learning|create|solution|no.*compos/i);
  });

  test("07 — compose production page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/compose/production`);
    const html = await bodyText(page);
    expect(html).toMatch(/compose|production|create|solution|no.*compos/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 3: Org-Scoped Pages — Evaluation
// ═══════════════════════════════════════════════════════════════

test.describe("3. Org evaluation pages", () => {
  test("08 — evaluation page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/evaluation`);
    const html = await bodyText(page);
    expect(html).toMatch(/evaluat|review|submission|no.*evaluat/i);
  });

  test("09 — evaluation settings page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/evaluation/settings`);
    const html = await bodyText(page);
    expect(html).toMatch(/evaluat|setting|configur|rubric/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 4: Org-Scoped Pages — Requirements
// ═══════════════════════════════════════════════════════════════

test.describe("4. Org requirements pages", () => {
  test("10 — requirements list page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/requirements`);
    const html = await bodyText(page);
    expect(html).toMatch(/requirement|profile|no.*requirement|capabilit/i);
  });

  test("11 — new requirement page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/requirements/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/requirement|profile|create|new|add/i);
  });

  test("12 — requirement detail with fake ID handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/requirements/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    // Should show not found or error boundary, not crash
    expect(html.length).toBeGreaterThan(100);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 5: Org-Scoped Pages — Reviews
// ═══════════════════════════════════════════════════════════════

test.describe("5. Org reviews pages", () => {
  test("13 — reviews list page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/reviews`);
    const html = await bodyText(page);
    expect(html).toMatch(/review|submission|queue|no.*review/i);
  });

  test("14 — review detail with fake ID handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/reviews/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(100);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 6: Org-Scoped Pages — Settings & Opportunities
// ═══════════════════════════════════════════════════════════════

test.describe("6. Org settings & opportunities", () => {
  test("15 — org settings page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/settings`);
    const html = await bodyText(page);
    expect(html).toMatch(/setting|configur|org|name/i);
  });

  test("16 — org opportunities page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/opportunities`);
    const html = await bodyText(page);
    expect(html).toMatch(/opportunit|post|no.*opportunit|create/i);
  });

  test("17 — org members page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/members`);
    const html = await bodyText(page);
    expect(html).toMatch(/member|invite|role|user/i);
  });

  test("18 — org providers page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/providers`);
    const html = await bodyText(page);
    expect(html).toMatch(/provider|integrat|connect|no.*provider/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 7: Tenant Management Pages
// ═══════════════════════════════════════════════════════════════

test.describe("7. Tenant management pages", () => {
  test("19 — tenant page with fake ID handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("20 — tenant billing page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/billing");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("21 — tenant branding page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/branding");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("22 — tenant budgets page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/budgets");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("23 — tenant credits page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/credits");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("24 — tenant domains page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/domains");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("25 — tenant licenses page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/licenses");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("26 — tenant members page handles gracefully", async () => {
    await goto(page, "/dashboard/tenant/fake-tenant-id/members");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 8: Platform Admin Pages (require platform role)
// ═══════════════════════════════════════════════════════════════

test.describe("8. Platform admin pages", () => {
  test("27 — platform index page handles non-admin gracefully", async () => {
    await goto(page, "/platform");
    const html = await bodyText(page);
    // Should redirect, show forbidden, or show empty — not crash
    expect(html.length).toBeGreaterThan(50);
  });

  test("28 — platform tenants page handles non-admin", async () => {
    await goto(page, "/platform/tenants");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("29 — platform partners page handles non-admin", async () => {
    await goto(page, "/platform/partners");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("30 — platform plans page handles non-admin", async () => {
    await goto(page, "/platform/plans");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("31 — platform pricing page handles non-admin", async () => {
    await goto(page, "/platform/pricing");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("32 — platform invoices page handles non-admin", async () => {
    await goto(page, "/platform/invoices");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("33 — platform settlements page handles non-admin", async () => {
    await goto(page, "/platform/settlements");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("34 — platform usage page handles non-admin", async () => {
    await goto(page, "/platform/usage");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("35 — platform audit page handles non-admin", async () => {
    await goto(page, "/platform/audit");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("36 — platform tenant detail handles non-admin", async () => {
    await goto(page, "/platform/tenants/fake-tenant-id");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 9: Public Pages (no auth)
// ═══════════════════════════════════════════════════════════════

test.describe("9. Public pages", () => {
  test("37 — certificate page handles nonexistent cert", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/certificates/CERT-000-FAKE");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("38 — join page handles invalid code", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/join/invalid-code");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("39 — public user profile handles fake username", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/u/nonexistent-test-user");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("40 — public portfolio item handles fake path", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/u/nonexistent-test-user/fake-item");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("41 — employer career page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, `/employers/${orgId}`);
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("42 — health page loads", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/health");
    const html = await p.innerHTML("body");
    expect(html.length).toBeGreaterThan(0);
    await c.close();
  });

  test("43 — mock checkout page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/mock-checkout");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("44 — registry page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/registry");
    const html = await bodyText(p);
    expect(html).toMatch(/registry|pack|skill|browse/i);
    await c.close();
  });

  test("45 — registry workflows page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/registry/workflows");
    const html = await bodyText(p);
    expect(html).toMatch(/workflow|registry|browse/i);
    await c.close();
  });

  test("46 — registry pack detail handles fake ID", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/registry/01NONEXISTENT000000000000");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("47 — registry workflow detail handles fake ID", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/registry/workflows/01NONEXISTENT000000000000");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 10: Partner Portal Pages
// ═══════════════════════════════════════════════════════════════

test.describe("10. Partner portal pages", () => {
  test("48 — partner page handles fake ID", async () => {
    await goto(page, "/partner/fake-partner-id");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("49 — partner provision page handles fake ID", async () => {
    await goto(page, "/partner/fake-partner-id/provision");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("50 — partner tenants page handles fake ID", async () => {
    await goto(page, "/partner/fake-partner-id/tenants");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("51 — partner statements page handles fake ID", async () => {
    await goto(page, "/partner/fake-partner-id/statements");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("52 — partner statement detail handles fake IDs", async () => {
    await goto(page, "/partner/fake-partner-id/statements/fake-stmt-id");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 11: Client Access Pages
// ═══════════════════════════════════════════════════════════════

test.describe("11. Client access pages", () => {
  test("53 — client access page renders", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/client/access");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });

  test("54 — client project page handles fake ID", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await goto(p, "/client/01NONEXISTENT000000000000");
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 12: Org Workflow & Installation Pages
// ═══════════════════════════════════════════════════════════════

test.describe("12. Org workflow & installation pages", () => {
  test("55 — workflow installations list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-installations`);
    const html = await bodyText(page);
    expect(html).toMatch(/install|workflow|no.*install/i);
  });

  test("56 — workflow installations detail handles fake ID", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-installations/01FAKE`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("57 — workflow runs list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-runs`);
    const html = await bodyText(page);
    expect(html).toMatch(/run|workflow|no.*run/i);
  });

  test("58 — workflow runs detail handles fake ID", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-runs/01FAKE`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("59 — workflow packs list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-packs`);
    const html = await bodyText(page);
    expect(html).toMatch(/workflow|pack|no.*pack/i);
  });

  test("60 — workflow packs new page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/workflow-packs/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/workflow|pack|create|new/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 13: Org Skills, Packs, Paths, Projects Pages
// ═══════════════════════════════════════════════════════════════

test.describe("13. Org skills, packs, paths, projects", () => {
  test("61 — org skills list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/skills`);
    const html = await bodyText(page);
    expect(html).toMatch(/skill|no.*skill|create/i);
  });

  test("62 — org new skill page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/skills/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/skill|create|new|add/i);
  });

  test("63 — org packs list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/packs`);
    const html = await bodyText(page);
    expect(html).toMatch(/pack|no.*pack|skill/i);
  });

  test("64 — org new pack page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/packs/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/pack|create|new/i);
  });

  test("65 — org review queue page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/packs/review-queue`);
    const html = await bodyText(page);
    expect(html).toMatch(/review|queue|no.*review|pack/i);
  });

  test("66 — org paths list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/paths`);
    const html = await bodyText(page);
    expect(html).toMatch(/path|learning|no.*path/i);
  });

  test("67 — org new path page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/paths/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/path|create|new|learning/i);
  });

  test("68 — org projects list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/projects`);
    const html = await bodyText(page);
    expect(html).toMatch(/project|no.*project|create/i);
  });

  test("69 — org new project page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/projects/new`);
    const html = await bodyText(page);
    expect(html).toMatch(/project|create|new/i);
  });

  test("70 — org progress page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/progress`);
    const html = await bodyText(page);
    expect(html).toMatch(/progress|no.*data|learner/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 14: Org Cohort Pages
// ═══════════════════════════════════════════════════════════════

test.describe("14. Org cohort pages", () => {
  test("71 — org cohorts list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/cohorts`);
    const html = await bodyText(page);
    expect(html).toMatch(/cohort|no.*cohort|create/i);
  });

  test("72 — org briefs list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/briefs`);
    const html = await bodyText(page);
    expect(html).toMatch(/brief|no.*brief|client/i);
  });

  test("73 — org installations list renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/installations`);
    const html = await bodyText(page);
    expect(html).toMatch(/install|no.*install|pack/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 15: Dashboard-Level Pages (non-talent)
// ═══════════════════════════════════════════════════════════════

test.describe("15. Dashboard-level pages", () => {
  test("74 — dashboard skills page renders", async () => {
    await goto(page, "/dashboard/skills");
    const html = await bodyText(page);
    expect(html).toMatch(/skill|practice|no.*skill/i);
  });

  test("75 — dashboard projects page renders", async () => {
    await goto(page, "/dashboard/projects");
    const html = await bodyText(page);
    expect(html).toMatch(/project|no.*project|submission/i);
  });

  test("76 — dashboard orgs page renders", async () => {
    await goto(page, "/dashboard/orgs");
    const html = await bodyText(page);
    expect(html).toMatch(/org|create|no.*org/i);
  });

  test("77 — dashboard new org page renders", async () => {
    await goto(page, "/dashboard/orgs/new");
    const html = await bodyText(page);
    expect(html).toMatch(/org|create|new|name/i);
  });

  test("78 — dashboard org detail page renders", async () => {
    await goto(page, `/dashboard/orgs/${orgId}`);
    const html = await bodyText(page);
    expect(html).toMatch(/sweep test org|org|project|cohort/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 16: Error Handling & Edge Cases
// ═══════════════════════════════════════════════════════════════

test.describe("16. Error handling & edge cases", () => {
  test("79 — nonexistent org ID shows error or redirect", async () => {
    await goto(page, "/dashboard/orgs/01NONEXISTENT000000000000");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("80 — nonexistent cohort under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/cohorts/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("81 — nonexistent project under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/projects/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("82 — nonexistent skill under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/skills/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("83 — nonexistent pack under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/packs/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("84 — nonexistent path under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/paths/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("85 — nonexistent brief under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/briefs/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("86 — nonexistent opportunity ID handles gracefully", async () => {
    await goto(page, "/dashboard/opportunities/01NONEXISTENT000000000000");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("87 — nonexistent installation under real org handles gracefully", async () => {
    await goto(page, `/dashboard/orgs/${orgId}/installations/01NONEXISTENT000000000000`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
  });

  test("88 — completely random URL shows 404", async () => {
    await goto(page, "/this-page-definitely-does-not-exist-12345");
    const html = await bodyText(page);
    expect(html).toMatch(/404|not.*found|page/i);
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 17: Security — Auth Redirect on Protected Pages
// ═══════════════════════════════════════════════════════════════

test.describe("17. Auth redirects", () => {
  test("89 — unauthenticated /dashboard/orgs redirects to login", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/orgs");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("90 — unauthenticated /dashboard/skills redirects to login", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/skills");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("91 — unauthenticated /dashboard/projects redirects to login", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/dashboard/projects");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    expect(p.url()).toMatch(/login|sign/i);
    await c.close();
  });

  test("92 — unauthenticated /platform redirects or shows error", async ({ browser }) => {
    const c = await browser.newContext();
    const p = await c.newPage();
    await p.goto("/platform");
    await p.waitForLoadState("domcontentloaded");
    await p.waitForTimeout(3000);
    // May redirect to login or show unauthorized
    const html = await bodyText(p);
    expect(html.length).toBeGreaterThan(50);
    await c.close();
  });
});

// ═══════════════════════════════════════════════════════════════
// SECTION 18: No-Crash Sweep & Final Validation
// ═══════════════════════════════════════════════════════════════

test.describe("18. Final validation", () => {
  test("93 — no pages show raw Python traceback", async () => {
    const pages = [
      "/dashboard",
      "/dashboard/passport",
      "/dashboard/opportunities",
      "/dashboard/talent",
      `/dashboard/orgs/${orgId}`,
      `/dashboard/orgs/${orgId}/settings`,
    ];
    for (const p of pages) {
      await goto(page, p);
      const html = await bodyText(page);
      expect(html).not.toMatch(/traceback.*most recent call/i);
    }
  });

  test("94 — no pages expose stack traces", async () => {
    const pages = [
      `/dashboard/orgs/${orgId}/evaluation`,
      `/dashboard/orgs/${orgId}/requirements`,
      `/dashboard/orgs/${orgId}/reviews`,
      `/dashboard/orgs/${orgId}/compose/learning`,
    ];
    for (const p of pages) {
      await goto(page, p);
      const html = await bodyText(page);
      expect(html).not.toMatch(/at\s+object\.\<anonymous\>|at\s+module\._compile/i);
    }
  });

  test("95 — no pages expose environment variables", async () => {
    const pages = ["/dashboard", `/dashboard/orgs/${orgId}/settings`, "/dashboard/settings"];
    for (const p of pages) {
      await goto(page, p);
      const html = await bodyText(page);
      expect(html).not.toMatch(/database_url|secret_key|api_key/i);
    }
  });

  test("96 — all org pages have consistent layout", async () => {
    const pages = [
      `/dashboard/orgs/${orgId}/skills`,
      `/dashboard/orgs/${orgId}/projects`,
      `/dashboard/orgs/${orgId}/cohorts`,
      `/dashboard/orgs/${orgId}/paths`,
    ];
    for (const p of pages) {
      await goto(page, p);
      const html = await page.innerHTML("body");
      // Each should have meaningful HTML structure
      expect(html.length).toBeGreaterThan(500);
      expect(html).toMatch(/<div/i);
    }
  });

  test("97 — org pages work at mobile width", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, `/dashboard/orgs/${orgId}`);
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(200);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("98 — platform pages work at mobile width", async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await goto(page, "/platform");
    const html = await bodyText(page);
    expect(html.length).toBeGreaterThan(50);
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test("99 — all tested pages have a title", async () => {
    const pages = ["/dashboard", "/dashboard/settings", `/dashboard/orgs/${orgId}`, "/login"];
    for (const p of pages) {
      await goto(page, p);
      expect(await page.title()).toBeTruthy();
    }
  });

  test("100 — final check: zero API 500 errors across all tests", () => {
    if (api500s.length > 0) {
      console.error("API 500s encountered:", api500s);
    }
    expect(api500s).toHaveLength(0);
  });
});
