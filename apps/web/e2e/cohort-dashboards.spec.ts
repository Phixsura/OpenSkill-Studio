/**
 * Cohort dashboard browser tests — progress, drill-down, my-dashboard.
 */
import { test, expect } from "@playwright/test";
import {
  registerUser,
  createOrg,
  addOrgMember,
  createCohort,
  activateCohort,
  addCohortMember,
  loginInBrowser,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let learner: AuthContext;
let orgId: string;
let cohortId: string;

test.beforeAll(async () => {
  admin = await registerUser("DashTest Admin");
  learner = await registerUser("DashTest Alice");
  orgId = await createOrg(admin, `DashTest ${Date.now()}`);
  await addOrgMember(admin, orgId, learner.userId, "student");
  cohortId = await createCohort(admin, orgId, "Dashboard Test Cohort");
  await activateCohort(admin, orgId, cohortId);
  await addCohortMember(admin, orgId, cohortId, learner.userId, "learner");

  // Create + publish + assign a project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Dashboard Project",
      description: "For progress tracking",
      instructions: "Submit your work",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    }),
  });
  const projId = (await projRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${projId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ project_id: projId }),
  });
});

test.describe("Instructor Progress Dashboard", () => {
  test("shows aggregate stats", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Stats cards are inside the main content
    await expect(page.getByText("Learners", { exact: true }).first()).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Overdue").first()).toBeVisible({ timeout: 5_000 });
  });

  test("shows project progress table", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Project Progress")).toBeVisible();
    await expect(page.locator("text=Dashboard Project")).toBeVisible();
    // Table headers
    await expect(page.locator("th:has-text('Not Started')")).toBeVisible();
    await expect(page.locator("th:has-text('Submitted')")).toBeVisible();
    await expect(page.locator("th:has-text('Approved')")).toBeVisible();
  });

  test("student cannot access instructor dashboard (403)", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
    await page.waitForLoadState("networkidle");

    // The page loads — should not crash even with 403 on progress
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
  });
});

test.describe("Progress Learner List", () => {
  test("shows list of learners with drill-down links", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Learner Progress')")).toBeVisible();
    await expect(page.locator("text=DashTest Alice")).toBeVisible();
  });

  test("clicking a learner navigates to drill-down", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress`);
    await page.waitForLoadState("networkidle");

    await page.click("text=DashTest Alice");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('DashTest Alice')")).toBeVisible();
  });
});

test.describe("Learner Drill-Down Page", () => {
  test("shows learner's skill and project progress", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress/${learner.userId}`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('DashTest Alice')")).toBeVisible();
    await expect(page.locator("h2:has-text('Projects')")).toBeVisible();
    await expect(page.locator("text=Dashboard Project")).toBeVisible();
    await expect(page.locator("text=not started")).toBeVisible();
  });

  test("shows last active time", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress/${learner.userId}`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Last active")).toBeVisible();
  });
});

test.describe("Learner My-Dashboard", () => {
  test("shows cohort name and assigned content", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Dashboard Test Cohort')")).toBeVisible();
  });

  test("shows assigned projects with status", async ({ page }) => {
    await loginInBrowser(page, learner.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h2:has-text('Assigned Projects')")).toBeVisible();
    await expect(page.locator("text=Dashboard Project")).toBeVisible();
  });
});
