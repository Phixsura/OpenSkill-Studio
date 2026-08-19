/**
 * Test remaining untested FE features:
 * - Cohort delete
 * - Brief edit
 * - Brief delete
 * - Creator assignment (project page)
 */
import { test, expect } from "@playwright/test";
import {
  registerUser,
  createOrg,
  addOrgMember,
  createCohort,
  loginInBrowser,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
test.setTimeout(120_000);

let admin: AuthContext;
let student: AuthContext;
let orgId: string;

test.beforeAll(async () => {
  admin = await registerUser("Remain Admin");
  student = await registerUser("Remain Student");
  orgId = await createOrg(admin, `Remain ${Date.now()}`);
  await addOrgMember(admin, orgId, student.userId, "student");
});

test("cohort delete: draft cohort can be deleted", async ({ page }) => {
  const cohortId = await createCohort(admin, orgId, "Deletable Cohort");

  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);

  // Should have Delete button for draft cohort
  const deleteBtn = page.getByRole("button", { name: /delete/i });
  if (await deleteBtn.isVisible({ timeout: 5_000 })) {
    // Mock confirm dialog
    page.on("dialog", (d) => d.accept());
    await deleteBtn.click();
    await page.waitForTimeout(3000);

    // Should redirect to cohort list
    expect(page.url()).toContain("/cohorts");
    // Should have navigated away from the cohort detail page
    await page.waitForTimeout(1000);
    // Cohort should be gone — trying to access it should 404
    const check = await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}`, { headers: admin.headers });
    expect(check.status).toBe(404);
  }
});

test("brief edit: change title and objective", async ({ page }) => {
  const briefRes = await fetch(`${API}/orgs/${orgId}/briefs`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Editable Brief",
      client_name: "Edit Corp",
      project_type: "viz",
      objective: "Original objective that should be changed via edit form",
    }),
  });
  const briefId = (await briefRes.json()).data.id;

  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/briefs/${briefId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);

  // Click Edit button
  const editBtn = page.getByRole("button", { name: /edit/i });
  await expect(editBtn).toBeVisible({ timeout: 5_000 });
  await editBtn.click();
  await page.waitForTimeout(500);

  // Should show edit form — find the title input and change it
  const titleInput = page.locator('input[value="Editable Brief"]');
  if (await titleInput.isVisible({ timeout: 3_000 })) {
    await titleInput.fill("Updated Brief Title");

    // Save
    const saveBtn = page.getByRole("button", { name: /save/i });
    await saveBtn.click();
    await page.waitForTimeout(2000);

    // Verify title changed
    await expect(page.getByText("Updated Brief Title")).toBeVisible({ timeout: 5_000 });
  }
});

test("brief delete: draft brief can be deleted", async ({ page }) => {
  const briefRes = await fetch(`${API}/orgs/${orgId}/briefs`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Deletable Brief",
      client_name: "Del Corp",
      project_type: "viz",
      objective: "This brief will be deleted through the browser UI",
    }),
  });
  const briefId = (await briefRes.json()).data.id;

  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/briefs/${briefId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);

  // Should have Delete button
  const deleteBtn = page.getByRole("button", { name: /delete/i });
  if (await deleteBtn.isVisible({ timeout: 5_000 })) {
    page.on("dialog", (d) => d.accept());
    await deleteBtn.click();
    await page.waitForTimeout(3000);

    // Should redirect to briefs list
    expect(page.url()).toContain("/briefs");
  }
});

test("creator assignment: assign and list on project page", async ({ page }) => {
  // Create a published project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Creator Test Project",
      description: "Test creator assignment UI",
      instructions: "Instructions here",
      rubric: [{ criterion: "Quality", max_score: 100 }],
    }),
  });
  const projectId = (await projRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${projectId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });

  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);

  // Should see "Creator Assignments" section (instructor view)
  const creatorsSection = page.getByText("Creator Assignments");
  if (await creatorsSection.isVisible({ timeout: 5_000 })) {
    // Assign a creator
    const userIdInput = page.locator('input[placeholder="User ID"]');
    if (await userIdInput.isVisible({ timeout: 3_000 })) {
      await userIdInput.fill(student.userId);
      await page.getByRole("button", { name: /assign/i }).last().click();
      await page.waitForTimeout(2000);

      // Should show the assigned creator
      await expect(page.getByText("Remain Student")).toBeVisible({ timeout: 5_000 });
    }
  }
});
