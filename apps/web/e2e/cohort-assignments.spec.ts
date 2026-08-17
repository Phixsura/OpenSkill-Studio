/**
 * Cohort skill + project assignment browser tests.
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
let orgId: string;
let cohortId: string;

test.beforeAll(async () => {
  admin = await registerUser("AssignTest Admin");
  orgId = await createOrg(admin, `AssignTest ${Date.now()}`);
  cohortId = await createCohort(admin, orgId, "Assignment Test Cohort");
  await activateCohort(admin, orgId, cohortId);

  // Create a skill via API
  const catRes = await fetch(`${API}/orgs/${orgId}/categories`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ name: "E2E Category" }),
  });
  const catId = (await catRes.json()).data.id;

  await fetch(`${API}/orgs/${orgId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      name: "E2E Skill",
      description: "A skill for E2E testing",
      difficulty: "beginner",
      category_id: catId,
    }),
  });

  // Create + publish a project via API
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "E2E Project",
      description: "A project for testing",
      instructions: "Complete the deliverables",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    }),
  });
  const projId = (await projRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${projId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });
});

test.describe("Skill Assignment Page", () => {
  test("shows assigned skills section", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Assigned Skills')")).toBeVisible();
  });

  test("shows available skills to assign", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Available Skills")).toBeVisible();
    await expect(page.locator("text=E2E Skill")).toBeVisible();
  });

  test("assign button is present for available skills", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("button:has-text('Assign')")).toBeVisible();
  });

  test("clicking assign adds skill to assigned list", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");

    await page.click("button:has-text('Assign')");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(500);

    // Should now appear in the assigned section with Remove button
    await expect(page.locator("button:has-text('Remove')")).toBeVisible();
  });
});

test.describe("Project Assignment Page", () => {
  test("shows assigned projects section", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Assigned Projects')")).toBeVisible();
  });

  test("shows project selector dropdown", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h2:has-text('Assign Project')")).toBeVisible();
    await expect(page.locator("select")).toBeVisible();
  });

  test("has deadline and max submissions override fields", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator('input[type="datetime-local"]')).toBeVisible();
    await expect(page.locator('input[type="number"]')).toBeVisible();
  });

  test("assign to cohort button is present", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("button:has-text('Assign to Cohort')")).toBeVisible();
  });
});
