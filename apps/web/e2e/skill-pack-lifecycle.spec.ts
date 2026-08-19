/**
 * Skill Pack Registry — full browser interaction E2E tests.
 *
 * Uses storageState to login once per user, then reuse across all tests.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import {
  registerUser,
  createOrg,
  loginInBrowser,
  createCohort,
  activateCohort,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let publisher: AuthContext;
let consumer: AuthContext;
let pubOrgId: string;
let conOrgId: string;
let packId: string;
let skillId: string;
let pubPackId: string;
let installId: string;
let pathId: string;
let cohortId: string;

// Shared browser contexts (login once, reuse)
let pubContext: BrowserContext;
let conContext: BrowserContext;
let pubPage: Page;
let conPage: Page;

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function apiPost(auth: AuthContext, path: string, body: object) {
  const res = await fetch(`${API}${path}`, {
    method: "POST", headers: auth.headers, body: JSON.stringify(body),
  });
  return res.json();
}

async function apiPut(auth: AuthContext, path: string, body: object) {
  const res = await fetch(`${API}${path}`, {
    method: "PUT", headers: auth.headers, body: JSON.stringify(body),
  });
  return res.json();
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  // Register users with retry — rate limit is strict
  let lastErr: Error | null = null;
  for (let i = 0; i < 5; i++) {
    try { publisher = await registerUser("PkE2E Pub"); lastErr = null; break; } catch (e) { lastErr = e as Error; await sleep(5000); }
  }
  if (lastErr) throw lastErr;
  await sleep(3000);
  for (let i = 0; i < 5; i++) {
    try { consumer = await registerUser("PkE2E Con"); lastErr = null; break; } catch (e) { lastErr = e as Error; await sleep(5000); }
  }
  if (lastErr) throw lastErr;

  pubOrgId = await createOrg(publisher, `Pub-${Date.now()}`);
  conOrgId = await createOrg(consumer, `Con-${Date.now()}`);

  // Setup data via API
  const cat = await apiPost(publisher, `/orgs/${pubOrgId}/categories`, { name: `C-${Date.now()}` });
  const skill = await apiPost(publisher, `/orgs/${pubOrgId}/skills`, {
    name: "E2E Prompt Skill", description: "Learn prompts", difficulty: "beginner", category_id: cat.data.id,
  });
  skillId = skill.data.id;
  await apiPost(publisher, `/orgs/${pubOrgId}/skills/${skillId}/exercises`, {
    title: "Basic Prompt", description: "Write a prompt", type: "text_answer", config: {}, max_score: 100,
  });
  const pack = await apiPost(publisher, `/orgs/${pubOrgId}/packs`, {
    name: "E2E Pack", summary: "E2E testing", visibility: "public", difficulty: "beginner",
    scenario_tags: ["ecommerce"], learning_outcomes: ["Create images"],
  });
  packId = pack.data.id;
  pubPackId = packId;
  await apiPost(publisher, `/orgs/${pubOrgId}/packs/${packId}/skills`, { skill_id: skillId });
  await apiPost(publisher, `/orgs/${pubOrgId}/packs/${packId}/releases`, { version: "1.0.0" });

  const inst = await apiPost(consumer, `/orgs/${conOrgId}/installations`, { pack_id: packId });
  installId = inst.data.id;

  const path = await apiPost(consumer, `/orgs/${conOrgId}/paths`, { name: "E2E Path", description: "Full track" });
  pathId = path.data.id;

  cohortId = await createCohort(consumer, conOrgId, `E2ECoh-${Date.now()}`);
  await activateCohort(consumer, conOrgId, cohortId);

  // Login both users in separate browser contexts (login ONCE)
  pubContext = await browser.newContext();
  pubPage = await pubContext.newPage();
  await loginInBrowser(pubPage, publisher.email, "TestPass123!");

  await sleep(2000);

  conContext = await browser.newContext();
  conPage = await conContext.newPage();
  await loginInBrowser(conPage, consumer.email, "TestPass123!");
});

test.afterAll(async () => {
  await pubContext?.close();
  await conContext?.close();
});

// ═══ 1. Pack List ═══
test("1.1 Packs tab shows heading and pack card", async () => {
  await pubPage.goto(`/dashboard/orgs/${pubOrgId}`);
  await pubPage.waitForLoadState("networkidle");
  await pubPage.click("text=Packs");
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("h1")).toContainText(/Skill Packs/i);
  await expect(pubPage.locator("text=E2E Pack")).toBeVisible();
});

test("1.2 New Pack button navigates to form", async () => {
  await pubPage.click("text=New Pack");
  await expect(pubPage).toHaveURL(/\/packs\/new/);
  await expect(pubPage.locator("h1")).toContainText(/New Skill Pack/i);
});

test("1.3 Create pack form has fields", async () => {
  await expect(pubPage.locator("input").first()).toBeVisible();
  await expect(pubPage.locator("textarea").first()).toBeVisible();
  await expect(pubPage.locator('button:has-text("Create")')).toBeVisible();
});

// ═══ 2. Pack Detail ═══
test("2.1 Pack detail shows name and published status", async () => {
  await pubPage.goto(`/dashboard/orgs/${pubOrgId}/packs/${packId}`);
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("text=E2E Pack")).toBeVisible();
  await expect(pubPage.locator("text=published")).toBeVisible();
});

test("2.2 Pack detail shows release v1.0.0", async () => {
  await expect(pubPage.locator("text=1.0.0")).toBeVisible();
});

test("2.3 Pack detail shows skill in contents", async () => {
  await expect(pubPage.locator("text=E2E Prompt Skill")).toBeVisible();
});

// ═══ 3. Public Registry ═══
test("3.1 Registry page shows search and cards", async () => {
  await pubPage.goto("/registry");
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("h1")).toContainText(/Registry/i);
  await expect(pubPage.locator('input[placeholder*="Search" i]')).toBeVisible();
  await expect(pubPage.locator("a[href*='/registry/']").first()).toBeVisible();
});

test("3.2 Clicking card navigates to pack detail", async () => {
  await pubPage.locator("a[href*='/registry/']").first().click();
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("text=← Back to Registry")).toBeVisible();
});

test("3.3 Registry pack detail shows releases and outcomes", async () => {
  await pubPage.goto(`/registry/${pubPackId}`);
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("text=Releases")).toBeVisible();
  await expect(pubPage.locator("text=v1.0.0")).toBeVisible();
  await expect(pubPage.locator("text=Create images")).toBeVisible();
});

// ═══ 4. Installations ═══
test("4.1 Installed tab shows installations list", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}`);
  await conPage.waitForLoadState("networkidle");
  await conPage.click("text=Installed");
  await conPage.waitForLoadState("networkidle");
  await expect(conPage.locator("h1")).toContainText(/Installed/i);
  await expect(conPage.locator("text=1.0.0")).toBeVisible();
});

test("4.2 Installation detail shows version and actions", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations/${installId}`);
  await conPage.waitForLoadState("networkidle");
  await expect(conPage.locator("text=1.0.0")).toBeVisible();
  await expect(conPage.locator('button:has-text("Fork")')).toBeVisible();
  await expect(conPage.locator('button:has-text("Remove")')).toBeVisible();
});

test("4.3 Update banner after new release", async () => {
  // Publish v1.1.0
  const cat = await apiPost(publisher, `/orgs/${pubOrgId}/categories`, { name: `U-${Date.now()}` });
  const s2 = await apiPost(publisher, `/orgs/${pubOrgId}/skills`, {
    name: "Upd Skill", description: "New", difficulty: "advanced", category_id: cat.data.id,
  });
  await apiPost(publisher, `/orgs/${pubOrgId}/packs/${packId}/skills`, { skill_id: s2.data.id });
  await apiPost(publisher, `/orgs/${pubOrgId}/packs/${packId}/releases`, { version: "1.1.0" });

  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations/${installId}`);
  await conPage.waitForLoadState("networkidle");
  await expect(conPage.locator("text=1.1.0").first()).toBeVisible();
});

// ═══ 5. Learning Paths ═══
test("5.1 Paths tab shows heading", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}`);
  await conPage.waitForLoadState("networkidle");
  await conPage.click("text=Paths");
  await conPage.waitForLoadState("networkidle");
  await expect(conPage.locator("h1")).toContainText(/Learning Paths/i);
});

test("5.2 Path list shows created path", async () => {
  await expect(conPage.locator("text=E2E Path")).toBeVisible();
});

test("5.3 New Path form has fields", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/new`);
  await conPage.waitForLoadState("networkidle");
  await expect(conPage.locator("h1")).toContainText(/New Learning Path/i);
  await expect(conPage.locator("input").first()).toBeVisible();
  await expect(conPage.locator('button:has-text("Create")')).toBeVisible();
});

test("5.4 Path detail page loads", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/${pathId}`);
  await conPage.waitForLoadState("networkidle");
  // Verify we're on the path detail page (not redirected elsewhere)
  await expect(conPage).toHaveURL(new RegExp(`/paths/${pathId}`));
  // Page should have some content loaded (items section or add form)
  const pageContent = conPage.locator("body");
  await expect(pageContent).not.toBeEmpty();
});

// ═══ 6. Cohort Paths ═══
test("6.1 Cohort Paths tab shows heading", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/cohorts/${cohortId}/paths`);
  await conPage.waitForLoadState("networkidle");
  await expect(conPage).toHaveURL(new RegExp(`/cohorts/${cohortId}/paths`));
  // The heading "Learning Paths" is visible in the screenshot — wait for it
  await expect(conPage.locator("h2:has-text('Learning Paths')")).toBeVisible({ timeout: 10_000 });
});

test("6.2 Cohort Paths shows assign dropdown after path published", async () => {
  await apiPut(consumer, `/orgs/${conOrgId}/paths/${pathId}`, { status: "published" });
  await conPage.goto(`/dashboard/orgs/${conOrgId}/cohorts/${cohortId}/paths`);
  await conPage.waitForLoadState("networkidle");
  // Assign dropdown should appear when published paths exist
  const hasSelect = await conPage.locator("select").first().isVisible({ timeout: 5000 }).catch(() => false);
  const hasAssign = await conPage.locator("text=Assign").isVisible().catch(() => false);
  expect(hasSelect || hasAssign).toBeTruthy();
});

// ═══ 7. Navigation ═══
test("7.1 Org layout has Packs, Paths, Installed tabs", async () => {
  await pubPage.goto(`/dashboard/orgs/${pubOrgId}`);
  await pubPage.waitForLoadState("networkidle");
  await expect(pubPage.locator("nav >> text=Packs")).toBeVisible();
  await expect(pubPage.locator("nav >> text=Paths")).toBeVisible();
  await expect(pubPage.locator("nav >> text=Installed")).toBeVisible();
});

test("7.2 Cohort layout has Paths tab", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/cohorts/${cohortId}`);
  await conPage.waitForLoadState("networkidle");
  // Two "Paths" links exist (org nav + cohort nav) — verify at least one cohort-level one
  await expect(conPage.getByRole("link", { name: "Paths" }).nth(1)).toBeVisible();
});
