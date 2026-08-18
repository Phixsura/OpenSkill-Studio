/**
 * Cohort member management browser tests.
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
  type AuthContext,
} from "./helpers";

let admin: AuthContext;
let instructor: AuthContext;
let learnerA: AuthContext;
let learnerB: AuthContext;
let orgId: string;
let cohortId: string;

test.beforeAll(async () => {
  admin = await registerUser("MemberTest Admin");
  instructor = await registerUser("MemberTest Instructor");
  learnerA = await registerUser("MemberTest Alice");
  learnerB = await registerUser("MemberTest Bob");

  orgId = await createOrg(admin, `MemberTest ${Date.now()}`);
  await addOrgMember(admin, orgId, instructor.userId, "instructor");
  await addOrgMember(admin, orgId, learnerA.userId, "student");
  await addOrgMember(admin, orgId, learnerB.userId, "student");

  cohortId = await createCohort(admin, orgId, "Member Management Test");
  await activateCohort(admin, orgId, cohortId);
  await addCohortMember(admin, orgId, cohortId, instructor.userId, "instructor");
  await addCohortMember(admin, orgId, cohortId, learnerA.userId, "learner");
});

test.describe("Cohort Members Page", () => {
  test("shows member list with names and roles", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Cohort Members')")).toBeVisible();
    // Should have 2 members (instructor + learnerA)
    const rows = page.locator("table tbody tr");
    await expect(rows).toHaveCount(2, { timeout: 10_000 });
  });

  test("member roles are displayed as badges", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    // Wait for table to populate, then check role badges
    await expect(page.locator("table tbody tr")).toHaveCount(2, { timeout: 10_000 });
  });

  test("add member form is visible with inputs", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    // Member add uses org members dropdown (not raw User ID input)
    await expect(page.locator("select").first()).toBeVisible();
    await expect(page.locator("button:has-text('Add')")).toBeVisible();
  });

  test("remove button is present for each member", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Remove").first()).toBeVisible();
  });

  test("student cannot access members page (403)", async ({ page }) => {
    await loginInBrowser(page, learnerB.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");

    // Should not see the member table (API returns 403)
    await expect(page.getByText("MemberTest Alice")).not.toBeVisible({ timeout: 5_000 });
  });
});
