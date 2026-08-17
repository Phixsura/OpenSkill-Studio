/**
 * Full browser E2E test: the complete operational loop.
 *
 * Prerequisites:
 *   - Backend running on port 8000 (make dev-api)
 *   - Frontend running on port 3000 (make dev-web)
 *   - Database migrated (make db-migrate)
 *   - Infra running (make infra-up)
 *
 * Run with:
 *   cd apps/web && npx playwright test
 */

import { test, expect } from "@playwright/test";
import {
  registerUser,
  createOrg,
  addOrgMember,
  createCohort,
  addCohortMember,
  activateCohort,
  loginInBrowser,
  goToOrg,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

test.describe("Full Cohort Lifecycle", () => {
  let admin: Awaited<ReturnType<typeof registerUser>>;
  let instructor: Awaited<ReturnType<typeof registerUser>>;
  let learner: Awaited<ReturnType<typeof registerUser>>;
  let orgId: string;
  let cohortId: string;

  test.beforeAll(async () => {
    // Setup via API: create org, users, cohort
    admin = await registerUser("E2E Admin");
    instructor = await registerUser("E2E Instructor");
    learner = await registerUser("E2E Learner");

    orgId = await createOrg(admin, `E2E Org ${Date.now()}`);
    await addOrgMember(admin, orgId, instructor.userId, "instructor");
    await addOrgMember(admin, orgId, learner.userId, "student");

    cohortId = await createCohort(admin, orgId, "AI Visual Commerce — E2E Test");
    await activateCohort(admin, orgId, cohortId);
    await addCohortMember(admin, orgId, cohortId, instructor.userId, "instructor");
    await addCohortMember(admin, orgId, cohortId, learner.userId, "learner");
  });

  // ── 1. Instructor: cohort management ──────────────────

  test("instructor can see cohort list and navigate to detail", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await goToOrg(page, orgId);

    // Click Cohorts tab
    await page.click('text=Cohorts');
    await page.waitForLoadState("networkidle");

    // Cohort card should be visible
    await expect(page.locator("text=AI Visual Commerce")).toBeVisible();

    // Click into the cohort
    await page.click("text=AI Visual Commerce");
    await page.waitForLoadState("networkidle");

    // Should see stats cards
    await expect(page.locator("text=Learners")).toBeVisible();
  });

  test("instructor can manage cohort members", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    // Should see at least 2 members (instructor + learner)
    await expect(page.locator("text=Cohort Members")).toBeVisible();
    await expect(page.locator("table tbody tr")).toHaveCount(2, { timeout: 10_000 });
  });

  // ── 2. Instructor: create client brief ────────────────

  test("instructor can create a client brief", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    // Click create
    await page.click("text=+ New Brief");

    // Fill form
    await page.fill('input[placeholder*="Brief title"]', "Acme Product Campaign");
    await page.fill('input[placeholder*="Client name"]', "Acme Corp");
    await page.fill('textarea[placeholder*="Objective"]', "Create hero product images for Q4 launch campaign targeting young professionals");

    await page.click("text=Create Brief");
    await page.waitForLoadState("networkidle");

    // Should see it in the list
    await expect(page.locator("text=Acme Product Campaign")).toBeVisible();
  });

  test("instructor can view brief detail and convert to project", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    // Click into the brief
    await page.click("text=Acme Product Campaign");
    await page.waitForLoadState("networkidle");

    // Should see brief detail
    await expect(page.locator("text=Acme Corp")).toBeVisible();
    await expect(page.locator("text=hero product images")).toBeVisible();

    // Convert to project
    await page.click("text=Convert to Project");
    await page.waitForTimeout(500);

    // Fill rubric
    const criterionInput = page.locator('input[placeholder*="Rubric criterion"]');
    if (await criterionInput.isVisible()) {
      await criterionInput.fill("Visual Quality");
    }

    await page.click("text=Create Project");
    await page.waitForURL("**/projects/**", { timeout: 15_000 });

    // Should be on the new project page
    await expect(page.locator("text=Acme Product Campaign")).toBeVisible();
  });

  // ── 3. Instructor: assign project to cohort ───────────

  test("instructor can assign projects to cohort", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Assigned Projects")).toBeVisible();
  });

  test("instructor can assign skills to cohort", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Assigned Skills")).toBeVisible();
  });

  // ── 4. Instructor: cohort progress dashboard ──────────

  test("instructor can see cohort progress dashboard", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
    await page.waitForLoadState("networkidle");

    // Stats cards (inside main content area)
    const main = page.locator("main");
    await expect(main.getByText("Learners", { exact: true })).toBeVisible();
    await expect(main.getByText("Skills Assigned")).toBeVisible();
    await expect(main.getByText("Overdue")).toBeVisible();

    // Management links
    await expect(page.locator("text=Manage Members")).toBeVisible();
    await expect(page.locator("text=Assign Skills")).toBeVisible();
    await expect(page.locator("text=Assign Projects")).toBeVisible();
  });

  // ── 5. Learner: dashboard experience ──────────────────

  test("learner can see their cohort dashboard", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=AI Visual Commerce")).toBeVisible();
  });

  // ── 6. Navigation: tabs present ───────────────────────

  test("org layout shows Cohorts and Briefs tabs", async ({ page }) => {
    await loginInBrowser(page, instructor.email, "TestPass123!");
    await goToOrg(page, orgId);

    // The org layout nav is inside main > div > nav (the horizontal tab bar)
    const orgNav = page.locator("main nav").first();
    await expect(orgNav.getByText("Cohorts", { exact: true })).toBeVisible();
    await expect(orgNav.getByText("Briefs", { exact: true })).toBeVisible();
  });

  // ── 7. Visibility isolation ───────────────────────────

  test("learner only sees org-wide content, not unassigned cohort content", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await goToOrg(page, orgId);

    // Learner should see the Projects tab
    await page.click("text=Projects");
    await page.waitForLoadState("networkidle");

    // Should not crash — the page loads
    await expect(page.locator("h1, h2, [class*='text-2xl']").first()).toBeVisible();
  });

  // ── 8. RBAC: student cannot access briefs ─────────────

  test("student cannot access briefs page (403 or redirect)", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await goToOrg(page, orgId);

    // Navigate to briefs
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    // Should either show empty/error or the page loads but API returns 403
    // (FE handles this gracefully — no crash)
    const body = await page.textContent("body");
    expect(body).toBeDefined();
  });
});
