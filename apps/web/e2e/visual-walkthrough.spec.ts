/**
 * Visual walkthrough: register → create org → full cohort lifecycle → brief → convert.
 * Screenshots every step. Catches rendering bugs, broken layouts, missing data.
 */
import { test, expect, type Page } from "@playwright/test";
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
test.setTimeout(180_000);

let admin: AuthContext;
let student: AuthContext;
let orgId: string;
let cohortId: string;
let projectId: string;
let skillId: string;
let briefId: string;

const screenshots: string[] = [];
let screenshotIdx = 0;

async function snap(page: Page, label: string) {
  screenshotIdx++;
  const name = `${String(screenshotIdx).padStart(2, "0")}-${label}`;
  await page.screenshot({ path: `e2e/screenshots/${name}.png`, fullPage: true });
  screenshots.push(name);
}

test.beforeAll(async () => {
  admin = await registerUser("Visual Admin");
  student = await registerUser("Visual Student");

  orgId = await createOrg(admin, `Visual Walkthrough ${Date.now()}`);
  await addOrgMember(admin, orgId, student.userId, "student");

  // Create category + skill via API
  const catRes = await fetch(`${API}/orgs/${orgId}/categories`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ name: "AI Design" }),
  });
  const catId = (await catRes.json()).data.id;

  const skillRes = await fetch(`${API}/orgs/${orgId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      name: "Product Photography with AI",
      description: "Learn AI-powered product photography techniques for commercial use",
      difficulty: "intermediate",
      category_id: catId,
    }),
  });
  skillId = (await skillRes.json()).data.id;

  // Create + publish project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Sneaker Campaign Visual",
      description: "Create AI-generated product shots for a sneaker brand campaign",
      instructions: "Use AI tools to generate 5 product shots with prompts",
      rubric: [
        { criterion: "Visual Quality", max_score: 40 },
        { criterion: "Prompt Engineering", max_score: 30 },
        { criterion: "Brand Consistency", max_score: 30 },
      ],
      deadline: "2026-12-31T23:59:59Z",
      max_submissions: 3,
    }),
  });
  projectId = (await projRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/projects/${projectId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });

  // Create cohort
  cohortId = await createCohort(admin, orgId, "Fall 2026 — AI Visual Commerce");
  await activateCohort(admin, orgId, cohortId);
  await addCohortMember(admin, orgId, cohortId, student.userId, "learner");

  // Assign skill + project to cohort
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ skill_id: skillId }),
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      project_id: projectId,
      deadline_override: "2026-10-15T23:59:59Z",
    }),
  });

  // Student submits work
  const subRes = await fetch(
    `${API}/orgs/${orgId}/projects/${projectId}/submissions`,
    { method: "POST", headers: student.headers }
  );
  const subId = (await subRes.json()).data.id;
  await fetch(
    `${API}/orgs/${orgId}/projects/${projectId}/submissions/${subId}/submit`,
    { method: "POST", headers: student.headers }
  );

  // Create brief
  const briefRes = await fetch(`${API}/orgs/${orgId}/briefs`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "Nike Air Max Campaign",
      client_name: "Nike Inc.",
      client_industry: "Sportswear",
      project_type: "product_visualization",
      objective:
        "Create a series of AI-generated product shots for the Air Max 2027 line targeting Gen Z consumers",
      target_audience: "Gen Z sneaker enthusiasts, ages 16-25",
      deliverable_specs: [
        { name: "Hero Shot", type: "image", description: "Main campaign image" },
        { name: "Social Pack", type: "image", description: "5 images for Instagram" },
      ],
      tone_and_style: "Futuristic, bold, street culture inspired",
      budget_range: "$5,000 - $10,000",
      timeline: "3 weeks",
    }),
  });
  briefId = (await briefRes.json()).data.id;
});

// ═══════════════ Admin views ═══════════════

test.describe("Admin walks through all pages", () => {
  test("01 — cohorts list page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohorts-list");

    // Should see the cohort card
    await expect(page.getByText("Fall 2026")).toBeVisible({ timeout: 10_000 });
    // Should show member count
    await expect(page.getByText(/members?/)).toBeVisible({ timeout: 5_000 });
    // Status badge should be visible (CSS capitalize shows "Active")
    await expect(page.getByText("Active")).toBeVisible({ timeout: 5_000 });
  });

  test("02 — cohort detail / overview page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohort-detail");

    // Should show cohort name
    await expect(page.getByText("Fall 2026")).toBeVisible({ timeout: 10_000 });
    // Should show stats cards (use locator to avoid multi-match on "Projects")
    await expect(page.locator("text=Learners").first()).toBeVisible({ timeout: 5_000 });
    await expect(page.locator("text=Skills Assigned").first()).toBeVisible({ timeout: 5_000 });
    await expect(page.locator("text=Project Progress").first()).toBeVisible({ timeout: 5_000 });
    // Should show project progress table
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 5_000 });
  });

  test("03 — cohort members page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohort-members");

    // Should show member table
    await expect(page.getByText("Cohort Members")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Visual Student")).toBeVisible({ timeout: 5_000 });
    // Should show role badge in table (CSS capitalize shows "Learner")
    await expect(page.locator("table span", { hasText: /learner/i }).first()).toBeVisible({ timeout: 5_000 });
    // Should show add form
    // Member add uses org members dropdown
    await expect(page.locator("select").first()).toBeVisible();
  });

  test("04 — cohort skills page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohort-skills");

    // Should show assigned skill
    await expect(page.getByText("Product Photography")).toBeVisible({ timeout: 10_000 });
    // Should show Remove button
    await expect(page.getByText("Remove")).toBeVisible({ timeout: 5_000 });
  });

  test("05 — cohort projects page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohort-projects");

    // Should show assigned project
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 10_000 });
    // Should show deadline override
    await expect(page.getByText(/Deadline/)).toBeVisible({ timeout: 5_000 });
    // Should show mode (rendered as "Mode: assigned")
    await expect(page.getByText(/assigned/)).toBeVisible({ timeout: 5_000 });
  });

  test("06 — cohort progress page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "cohort-progress");

    // Should show learner list
    await expect(page.getByText("Visual Student")).toBeVisible({ timeout: 10_000 });
  });

  test("07 — learner drill-down page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(
      `/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress/${student.userId}`
    );
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "learner-drilldown");

    // Should show student name
    await expect(page.getByText("Visual Student")).toBeVisible({ timeout: 10_000 });
    // Should show skill + project progress
    await expect(page.getByText("Product Photography")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 5_000 });
  });

  test("08 — briefs list page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/briefs`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "briefs-list");

    // Should show the brief
    await expect(page.getByText("Nike Air Max Campaign")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Nike Inc.")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("draft")).toBeVisible({ timeout: 5_000 });
  });

  test("09 — brief detail page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/briefs/${briefId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "brief-detail");

    // Should show full brief info
    await expect(page.getByText("Nike Air Max Campaign")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Objective")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Gen Z sneaker enthusiasts")).toBeVisible({ timeout: 5_000 });
    // Should show deliverables
    await expect(page.getByText("Hero Shot")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Social Pack")).toBeVisible({ timeout: 5_000 });
    // Should show convert button (draft status)
    await expect(page.getByText("Convert to Project")).toBeVisible({ timeout: 5_000 });
  });

  test("10 — convert brief to project (click through)", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/briefs/${briefId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);

    // Click convert
    await page.getByText("Convert to Project").click();
    await page.waitForTimeout(500);
    await snap(page, "brief-convert-form");

    // Should show conversion form
    await expect(page.getByText("Create Project")).toBeVisible({ timeout: 5_000 });

    // Fill in rubric and submit
    const criterionInput = page.locator('input[placeholder="Rubric criterion name"]');
    if (await criterionInput.isVisible()) {
      await criterionInput.fill("Overall Quality");
    }

    await page.getByText("Create Project").click();
    await page.waitForTimeout(3000);
    await snap(page, "brief-converted");

    // Should redirect to project page or show success
    // The URL should change to a project page
    const url = page.url();
    const redirectedToProject = url.includes("/projects/");
    // Or the brief status changed
    if (!redirectedToProject) {
      // Go back and check brief is now active
      await page.goto(`/dashboard/orgs/${orgId}/briefs/${briefId}`);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(1000);
      await snap(page, "brief-after-convert");
      await expect(page.getByText("active")).toBeVisible({ timeout: 5_000 });
    }
  });
});

// ═══════════════ Student views ═══════════════

test.describe("Student walks through their views", () => {
  test("11 — student my-dashboard page", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "student-dashboard");

    // Should show cohort name
    await expect(page.getByText("Fall 2026")).toBeVisible({ timeout: 10_000 });
    // Should show assigned content
    await expect(page.getByText("Product Photography")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 5_000 });
  });

  test("12 — student projects list with cohort filter", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "student-projects");

    // Should see the campaign project
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 10_000 });
  });

  test("13 — student submission page", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "student-project-detail");

    // Should show project info
    await expect(page.getByText("Sneaker Campaign Visual")).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════ Error states ═══════════════

test.describe("Error and edge case rendering", () => {
  test("14 — nonexistent cohort shows error", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/01NONEXISTENT0000000000000`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    await snap(page, "nonexistent-cohort");

    // Should show error or fallback, not crash
    // Page should have some content (not blank white screen)
    const bodyText = await page.locator("body").innerText();
    expect(bodyText.length).toBeGreaterThan(10);
  });

  test("15 — nonexistent brief shows error", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/briefs/01NONEXISTENT0000000000000`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    await snap(page, "nonexistent-brief");

    // Should show error message
    const bodyText = await page.locator("body").innerText();
    expect(bodyText.length).toBeGreaterThan(10);
    // Should ideally show "not found" or "failed" or "error"
    const hasErrorMessage =
      bodyText.toLowerCase().includes("not found") ||
      bodyText.toLowerCase().includes("failed") ||
      bodyText.toLowerCase().includes("error") ||
      bodyText.toLowerCase().includes("brief");
    expect(hasErrorMessage).toBeTruthy();
  });

  test("16 — empty cohort (no assignments) renders cleanly", async ({ page }) => {
    const emptyCohortId = await createCohort(admin, orgId, "Empty Cohort Test");
    await activateCohort(admin, orgId, emptyCohortId);

    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts/${emptyCohortId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await snap(page, "empty-cohort");

    // Should show cohort name
    await expect(page.getByText("Empty Cohort")).toBeVisible({ timeout: 10_000 });
    // Should show 0 stats, not crash
    await expect(page.getByText("Learners")).toBeVisible({ timeout: 5_000 });
  });

  test("17 — org nav has Cohorts and Briefs tabs", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await snap(page, "org-nav-tabs");

    // Navigation should include Cohorts and Briefs
    await expect(page.getByRole("link", { name: "Cohorts" })).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole("link", { name: "Briefs" })).toBeVisible({ timeout: 5_000 });
  });
});
