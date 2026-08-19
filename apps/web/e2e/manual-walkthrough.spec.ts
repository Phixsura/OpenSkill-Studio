/**
 * Manual walkthrough with screenshots — captures every key screen
 * for visual verification of the deployed application.
 *
 * Run with: npx playwright test e2e/manual-walkthrough.spec.ts --headed
 * Screenshots saved to: e2e/screenshots/
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
let instructor: AuthContext;
let learner: AuthContext;
let orgId: string;
let cohortId: string;

test.beforeAll(async () => {
  admin = await registerUser("Demo Admin");
  instructor = await registerUser("Demo Instructor");
  learner = await registerUser("Demo Alice");
  orgId = await createOrg(admin, `Demo Org ${Date.now()}`);
  await addOrgMember(admin, orgId, instructor.userId, "instructor");
  await addOrgMember(admin, orgId, learner.userId, "student");
  cohortId = await createCohort(admin, orgId, "AI Visual Commerce — Fall 2026");
  await activateCohort(admin, orgId, cohortId);
  await addCohortMember(admin, orgId, cohortId, instructor.userId, "instructor");
  await addCohortMember(admin, orgId, cohortId, learner.userId, "learner");

  // Create skill + exercise
  const catRes = await fetch(`${API}/orgs/${orgId}/categories`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ name: "AI Production" }),
  });
  const catId = (await catRes.json()).data.id;
  const skRes = await fetch(`${API}/orgs/${orgId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      name: "Prompt Engineering",
      description: "Master AI prompt design",
      difficulty: "intermediate",
      category_id: catId,
    }),
  });
  const skId = (await skRes.json()).data.id;
  await fetch(`${API}/orgs/${orgId}/skills/${skId}/publish`, {
    method: "POST",
    headers: admin.headers,
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/skills`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ skill_id: skId }),
  });

  // Create + publish + assign project
  const projRes = await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({
      title: "AI Product Advertisement",
      description: "Create a complete AI-generated product advertisement",
      instructions: "Work through the production pipeline stage by stage",
      rubric: [
        { criterion: "Brief Alignment", max_score: 30 },
        { criterion: "Visual Quality", max_score: 40 },
        { criterion: "Commercial Readiness", max_score: 30 },
      ],
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

test("1. Instructor: org overview with Cohorts + Briefs tabs", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/01-org-overview.png", fullPage: true });
  await expect(page.locator("main nav").first().getByText("Cohorts")).toBeVisible();
});

test("2. Instructor: cohort list page", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/02-cohort-list.png", fullPage: true });
  await expect(page.getByText("AI Visual Commerce")).toBeVisible();
});

test("3. Instructor: cohort detail with stats", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: "e2e/screenshots/03-cohort-detail.png", fullPage: true });
  await expect(page.getByText("Learners", { exact: true }).first()).toBeVisible();
});

test("4. Instructor: cohort members page", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/04-cohort-members.png", fullPage: true });
  await expect(page.locator("table tbody tr")).toHaveCount(2, { timeout: 10_000 });
});

test("5. Instructor: skill assignment page", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/05-cohort-skills.png", fullPage: true });
  await expect(page.getByText("Prompt Engineering")).toBeVisible();
});

test("6. Instructor: project assignment page", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/06-cohort-projects.png", fullPage: true });
  await expect(page.getByText("AI Product Advertisement")).toBeVisible();
});

test("7. Instructor: progress learner list", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/07-progress-list.png", fullPage: true });
  await expect(page.getByText("Demo Alice")).toBeVisible();
});

test("8. Instructor: learner drill-down", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress/${learner.userId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/08-learner-drilldown.png", fullPage: true });
  await expect(page.getByText("Demo Alice")).toBeVisible();
  await expect(page.getByText("AI Product Advertisement")).toBeVisible();
});

test("9. Instructor: create client brief", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await page.waitForLoadState("networkidle");
  await page.click("text=+ New Brief");
  await page.fill('input[placeholder*="Brief title"]', "Acme Q4 Product Campaign");
  await page.fill('input[placeholder*="Client name"]', "Acme Corporation");
  await page.fill(
    'textarea[placeholder*="Objective"]',
    "Create hero images for Q4 product launch"
  );
  await page.screenshot({ path: "e2e/screenshots/09-brief-create-form.png", fullPage: true });
  await page.click("button:has-text('Create Brief')");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/10-brief-list-after-create.png", fullPage: true });
  await expect(page.getByText("Acme Q4 Product Campaign")).toBeVisible();
});

test("10. Instructor: brief detail + convert button", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await page.waitForLoadState("networkidle");
  await page.click("text=Acme Q4 Product Campaign");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/11-brief-detail.png", fullPage: true });
  await expect(page.getByText("Acme Corporation")).toBeVisible();
  await expect(page.locator("button:has-text('Convert to Project')")).toBeVisible();
});

test("11. Learner: my-dashboard view", async ({ page }) => {
  await loginInBrowser(page, learner.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/12-learner-dashboard.png", fullPage: true });
  await expect(page.getByText("AI Visual Commerce")).toBeVisible();
});

test("12. Learner: projects page with cohort filter", async ({ page }) => {
  await loginInBrowser(page, learner.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: "e2e/screenshots/13-learner-projects.png", fullPage: true });
  await expect(page.getByText("AI Product Advertisement")).toBeVisible();
  await expect(page.getByText("Filter by cohort")).toBeVisible();
});

test("13. Evaluation page shows multimodal type icons", async ({ page }) => {
  await loginInBrowser(page, instructor.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/evaluation`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: "e2e/screenshots/14-evaluation-page.png", fullPage: true });
  // Page should load without crash
  await expect(page.locator("h1, h2").first()).toBeVisible();
});
