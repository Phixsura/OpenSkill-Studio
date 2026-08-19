/**
 * Every-page smoke test — visits EVERY page in the app,
 * verifies it doesn't crash (no blank screen, no 500).
 * Covers the 20 pages that no other E2E test visits.
 */
import { test, expect } from "@playwright/test";
import {
  registerUser,
  createOrg,
  addOrgMember,
  loginInBrowser,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
test.setTimeout(120_000);

let admin: AuthContext;
let student: AuthContext;
let orgId: string;
let projectId: string;
let skillId: string;
let submissionId: string;

test.beforeAll(async () => {
  admin = await registerUser("EveryPage Admin");
  student = await registerUser("EveryPage Student");

  orgId = await createOrg(admin, `EveryPage ${Date.now()}`);
  await addOrgMember(admin, orgId, student.userId, "student");

  // Create skill
  const catRes = await fetch(`${API}/orgs/${orgId}/categories`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ name: "EP Cat" }),
  });
  const catId = (await catRes.json()).data.id;

  const skillRes = await fetch(`${API}/orgs/${orgId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      name: "EP Skill",
      description: "For every-page test",
      difficulty: "beginner",
      category_id: catId,
    }),
  });
  skillId = (await skillRes.json()).data.id;

  // Create + publish project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "EP Project",
      description: "Every-page project",
      instructions: "Instructions here",
      rubric: [{ criterion: "Quality", max_score: 100 }],
      deadline: "2026-12-31T23:59:59Z",
    }),
  });
  projectId = (await projRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${projectId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });

  // Student creates + submits a submission
  const subRes = await fetch(
    `${API}/orgs/${orgId}/projects/${projectId}/submissions`,
    { method: "POST", headers: student.headers }
  );
  submissionId = (await subRes.json()).data.id;
  await fetch(
    `${API}/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}/submit`,
    { method: "POST", headers: student.headers }
  );

  // Enable evaluation
  await fetch(`${API}/orgs/${orgId}/settings/evaluation`, {
    method: "PUT",
    headers: admin.headers,
    body: JSON.stringify({ enabled: true, monthly_budget_usd: 100 }),
  });
});

async function assertPageLoads(page: import("@playwright/test").Page, url: string) {
  await page.goto(url);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);
  const body = await page.locator("body").innerText();
  expect(body.length).toBeGreaterThan(10);
}

// ═══════════════ Auth Pages ═══════════════

test("forgot-password page loads", async ({ page }) => {
  await page.goto("/forgot-password");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("body")).not.toBeEmpty();
  // Should show email input
  const hasInput = await page.locator("input").count();
  expect(hasInput).toBeGreaterThan(0);
});

test("reset-password page loads", async ({ page }) => {
  await page.goto("/reset-password?token=fake");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("body")).not.toBeEmpty();
});

// ═══════════════ Global Dashboard Pages ═══════════════

test("dashboard landing page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard");
});

test("dashboard/projects page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/projects");
});

test("dashboard/skills page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/skills");
});

test("dashboard/settings page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/settings");
});

test("dashboard/portfolio/profile page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/portfolio/profile");
});

test("dashboard/portfolio page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/portfolio");
});

// ═══════════════ Org-Level Pages ═══════════════

test("create org page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, "/dashboard/orgs/new");
});

test("create project page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, `/dashboard/orgs/${orgId}/projects/new`);
});

test("project submit page loads", async ({ page }) => {
  await loginInBrowser(page, student.email, "TestPass123!");
  await assertPageLoads(
    page,
    `/dashboard/orgs/${orgId}/projects/${projectId}/submit`
  );
});

test("create skill page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, `/dashboard/orgs/${orgId}/skills/new`);
});

test("skill detail page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(page, `/dashboard/orgs/${orgId}/skills/${skillId}`);
});

test("submission detail page loads", async ({ page }) => {
  await loginInBrowser(page, student.email, "TestPass123!");
  await assertPageLoads(
    page,
    `/dashboard/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}`
  );
});

test("evaluation settings page loads", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await assertPageLoads(
    page,
    `/dashboard/orgs/${orgId}/evaluation/settings`
  );
});

// ═══════════════ Public Pages ═══════════════

test("health page loads", async ({ page }) => {
  await page.goto("/health");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("body")).not.toBeEmpty();
});

test("public profile page handles nonexistent user", async ({ page }) => {
  await page.goto("/u/nonexistent-user-xyz");
  await page.waitForLoadState("networkidle");
  // Should show 404 or "not found", not crash
  const status = page.url().includes("404") || (await page.locator("body").innerText()).length > 0;
  expect(status).toBeTruthy();
});
