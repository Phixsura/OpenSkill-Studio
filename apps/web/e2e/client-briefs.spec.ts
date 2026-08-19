/**
 * Client brief browser tests — list, create, detail, convert.
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
  admin = await registerUser("BriefTest Admin");
  student = await registerUser("BriefTest Student");
  orgId = await createOrg(admin, `BriefTest ${Date.now()}`);
  await addOrgMember(admin, orgId, student.userId, "student");
});

test.describe("Brief List Page", () => {
  test("shows empty state initially", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=No client briefs")).toBeVisible();
  });

  test("create brief via inline form", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    await page.click("text=+ New Brief");
    await page.fill('input[placeholder*="Brief title"]', "Acme Q4 Campaign");
    await page.fill('input[placeholder*="Client name"]', "Acme Corporation");
    await page.fill('textarea[placeholder*="Objective"]', "Create hero images for the Q4 product launch targeting young professionals 25-40");
    await page.click("button:has-text('Create Brief')");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Acme Q4 Campaign")).toBeVisible();
  });

  test("brief card shows client name and status", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Acme Corporation")).toBeVisible();
    await expect(page.locator("text=draft").first()).toBeVisible();
  });

  test("student cannot see briefs page content", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");

    // API returns 403, FE should not show brief data
    await expect(page.getByText("Acme Q4 Campaign")).not.toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Brief Detail Page", () => {
  test("shows full brief detail", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");
    await page.click("text=Acme Q4 Campaign");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("h1:has-text('Acme Q4 Campaign')")).toBeVisible();
    await expect(page.locator("text=Acme Corporation")).toBeVisible();
    await expect(page.locator("text=hero images")).toBeVisible();
  });

  test("shows Convert to Project button for draft briefs", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");
    await page.click("text=Acme Q4 Campaign");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("button:has-text('Convert to Project')")).toBeVisible();
  });

  test("convert form shows rubric and deadline fields", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");
    await page.click("text=Acme Q4 Campaign");
    await page.waitForLoadState("networkidle");

    await page.click("button:has-text('Convert to Project')");
    await page.waitForTimeout(300);

    await expect(page.locator('input[placeholder*="Rubric criterion"]')).toBeVisible();
    await expect(page.locator('input[type="number"]')).toBeVisible(); // max score
    await expect(page.locator('input[type="datetime-local"]')).toBeVisible();
    await expect(page.locator("button:has-text('Create Project')")).toBeVisible();
  });

  test("converting brief navigates to new project page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await goToOrg(page, orgId);
    await page.click("text=Briefs");
    await page.waitForLoadState("networkidle");
    await page.click("text=Acme Q4 Campaign");
    await page.waitForLoadState("networkidle");

    await page.click("button:has-text('Convert to Project')");
    await page.waitForTimeout(300);
    await page.click("button:has-text('Create Project')");
    await page.waitForURL("**/projects/**", { timeout: 15_000 });

    // Should land on the new project page
    await expect(page.locator("text=Acme Q4 Campaign")).toBeVisible();
  });
});
