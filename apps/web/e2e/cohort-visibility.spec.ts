/**
 * Cohort visibility + cohort filter browser tests.
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
  goToOrg,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let learnerInCohort: AuthContext;
let learnerOutside: AuthContext;
let orgId: string;
let cohortId: string;

test.beforeAll(async () => {
  admin = await registerUser("VisTest Admin");
  learnerInCohort = await registerUser("VisTest InCohort");
  learnerOutside = await registerUser("VisTest Outside");
  orgId = await createOrg(admin, `VisTest ${Date.now()}`);
  await addOrgMember(admin, orgId, learnerInCohort.userId, "student");
  await addOrgMember(admin, orgId, learnerOutside.userId, "student");

  cohortId = await createCohort(admin, orgId, "Visibility Test Cohort");
  await activateCohort(admin, orgId, cohortId);
  await addCohortMember(admin, orgId, cohortId, learnerInCohort.userId, "learner");

  // Create + publish + assign a cohort-only project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Cohort Only Project",
      description: "Only for cohort members",
      instructions: "Do the work",
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

  // Create an org-wide project (no cohort assignment)
  const owRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Org Wide Project",
      description: "For everyone",
      instructions: "All members",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    }),
  });
  const owId = (await owRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${owId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });
});

test.describe("Project Visibility", () => {
  test("cohort member sees org-wide + cohort project", async ({ page }) => {
    await loginInBrowser(page, learnerInCohort.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000); // wait for react-query

    await expect(page.getByText("Org Wide Project")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Cohort Only Project")).toBeVisible({ timeout: 5_000 });
  });

  test("outside learner sees only org-wide, not cohort project", async ({ page }) => {
    await loginInBrowser(page, learnerOutside.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    await expect(page.getByText("Org Wide Project")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Cohort Only Project")).not.toBeVisible({ timeout: 3_000 });
  });

  test("admin sees all projects regardless", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    await expect(page.getByText("Org Wide Project")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Cohort Only Project")).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Cohort Filter on Projects", () => {
  test("cohort filter dropdown is visible for cohort members", async ({ page }) => {
    await loginInBrowser(page, learnerInCohort.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    await expect(page.getByText("Filter by cohort")).toBeVisible({ timeout: 10_000 });
  });

  test("my-cohorts endpoint populates the filter", async ({ page }) => {
    await loginInBrowser(page, learnerInCohort.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // The filter should have at least "All projects" + cohort name
    await expect(page.getByText("Filter by cohort")).toBeVisible({ timeout: 10_000 });
    // Cohort name is inside a <select> <option> — check it exists via locator
    const options = page.locator("select option");
    const count = await options.count();
    expect(count).toBeGreaterThanOrEqual(2); // "All projects" + at least one cohort
  });
});

test.describe("Nav Tabs", () => {
  test("org layout has Cohorts and Briefs tabs", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);

    const orgNav = page.locator("main nav").first();
    await expect(orgNav.getByText("Cohorts", { exact: true })).toBeVisible();
    await expect(orgNav.getByText("Briefs", { exact: true })).toBeVisible();
  });
});
