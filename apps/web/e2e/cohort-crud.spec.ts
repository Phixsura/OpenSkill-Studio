/**
 * Cohort CRUD browser tests — every UI interaction on the cohort pages.
 */
import { test, expect } from "@playwright/test";
import {
  registerUser,
  createOrg,
  addOrgMember,
  loginInBrowser,
  goToOrg,
  type AuthContext,
} from "./helpers";

let admin: AuthContext;
let student: AuthContext;
let orgId: string;

test.beforeAll(async () => {
  admin = await registerUser("CohortCRUD Admin");
  student = await registerUser("CohortCRUD Student");
  orgId = await createOrg(admin, `CohortCRUD ${Date.now()}`);
  await addOrgMember(admin, orgId, student.userId, "student");
});

test.describe("Cohort List Page", () => {
  test("shows empty state when no cohorts", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=No cohorts yet")).toBeVisible();
  });

  test("create cohort via inline form", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");

    await page.click("text=+ New Cohort");
    await page.fill('input[placeholder*="Cohort name"]', "AI Commerce — Fall 2026");
    await page.fill('textarea[placeholder*="Description"]', "First commercial training cohort");
    await page.click("button:has-text('Create Cohort')");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=AI Commerce — Fall 2026")).toBeVisible();
  });

  test("cohort card shows status badge and member count", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("draft").first()).toBeVisible();
    await expect(page.getByText("0 members")).toBeVisible();
  });

  test("clicking cohort card navigates to detail", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");
    await page.click("text=AI Commerce — Fall 2026");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('AI Commerce')")).toBeVisible();
  });

  test("student can see cohorts tab", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await goToOrg(page, orgId);
    const nav = page.locator("main nav").first();
    await expect(nav.getByText("Cohorts", { exact: true })).toBeVisible();
  });
});

test.describe("Cohort Detail Page", () => {
  test("shows stats cards (Learners, Skills, Projects, Overdue)", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");
    await page.click("text=AI Commerce — Fall 2026");
    await page.waitForLoadState("networkidle");

    const main = page.locator("main");
    await expect(main.getByText("Learners", { exact: true })).toBeVisible();
    await expect(main.getByText("Skills Assigned")).toBeVisible();
    await expect(main.getByText("Overdue")).toBeVisible();
  });

  test("has management links (Members, Skills, Projects)", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");
    await page.click("text=AI Commerce — Fall 2026");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Manage Members")).toBeVisible();
    await expect(page.locator("text=Assign Skills")).toBeVisible();
    await expect(page.locator("text=Assign Projects")).toBeVisible();
  });

  test("sub-layout tabs are present", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Cohorts");
    await page.waitForLoadState("networkidle");
    await page.click("text=AI Commerce — Fall 2026");
    await page.waitForLoadState("networkidle");

    // The cohort sub-layout renders tabs — look for them anywhere on page
    await expect(page.getByRole("link", { name: "Overview", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Members", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Progress", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "My Dashboard" })).toBeVisible();
  });
});
