/**
 * Real user simulation — walks through the ENTIRE flow as a human would,
 * with slowMo, real form interactions, page-by-page navigation.
 *
 * This is NOT an assertion-heavy test. It simulates a real user session
 * and captures screenshots at every meaningful step for visual review.
 *
 * Run: E2E_API_URL=http://127.0.0.1:8000/api/v1 npx playwright test e2e/real-user-test.spec.ts --headed
 */
import { test, expect, type Page } from "@playwright/test";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
const ss = (name: string) => `e2e/screenshots/manual-${name}.png`;

// Full walkthrough — no slowMo for speed, screenshots at every step
test.setTimeout(120_000); // 2 minutes

let adminEmail: string;
let instructorEmail: string;
let aliceEmail: string;
let bobEmail: string;
const password = "TestPass123!";

test("Complete manual user flow", async ({ page }) => {
  // ═══════════════════════════════════════════
  // STEP 1: Register admin
  // ═══════════════════════════════════════════
  adminEmail = `admin-${Date.now()}@test.com`;
  await page.goto("/register");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: ss("01-register-page"), fullPage: true });

  await page.getByLabel("Name").fill("Admin Wang");
  await page.getByLabel("Email").fill(adminEmail);
  await page.getByLabel("Password").fill(password);
  await page.screenshot({ path: ss("02-register-filled"), fullPage: true });

  await page.getByRole("button", { name: "Sign up" }).click();
  await page.waitForURL("**/dashboard**", { timeout: 15000 });
  await page.screenshot({ path: ss("03-dashboard-after-register"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 2: Create organization
  // ═══════════════════════════════════════════
  await page.click("text=Organizations");
  await page.waitForLoadState("networkidle");

  // Look for new org button/link
  const newOrgLink = page.locator("text=New Organization, a[href*='new'], button:has-text('New')").first();
  if (await newOrgLink.isVisible()) {
    await newOrgLink.click();
    await page.waitForLoadState("networkidle");
  }
  await page.screenshot({ path: ss("04-orgs-page"), fullPage: true });

  // Create org via API (FE might need a different flow)
  const orgRes = await fetch(`${API}/orgs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "AI 视觉培训中心" }),
  });
  // Need auth token - get it from the page
  // Actually, let's register via API for speed and use browser for navigation

  // Register all users via API
  const register = async (email: string, name: string) => {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, display_name: name }),
    });
    return res.json();
  };

  instructorEmail = `inst-${Date.now()}@test.com`;
  aliceEmail = `alice-${Date.now()}@test.com`;
  bobEmail = `bob-${Date.now()}@test.com`;

  const adminData = await register(`admin2-${Date.now()}@test.com`, "Admin Wang");
  const instData = await register(instructorEmail, "Instructor Li");
  const aliceData = await register(aliceEmail, "Alice Chen");
  const bobData = await register(bobEmail, "Bob Zhang");

  const adminAuth = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${adminData.access_token}`
  };

  // Create org
  const org = await (await fetch(`${API}/orgs`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ name: `AI视觉培训 ${Date.now()}` }),
  })).json();
  const orgId = org.data.id;

  // Add members
  for (const [u, role] of [
    [instData.user.id, "instructor"],
    [aliceData.user.id, "student"],
    [bobData.user.id, "student"],
  ] as const) {
    await fetch(`${API}/orgs/${orgId}/members`, {
      method: "POST",
      headers: adminAuth,
      body: JSON.stringify({ user_id: u, role }),
    });
  }

  // ═══════════════════════════════════════════
  // STEP 3: Login as instructor, navigate to org
  // ═══════════════════════════════════════════
  // Clear previous auth state
  await page.context().clearCookies();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByLabel('Email').fill(instructorEmail);
  await page.getByLabel('Password').fill(password);
  await page.getByRole("button", { name: /sign|log/i }).first().click();
  await page.waitForURL("**/dashboard**", { timeout: 10000 });
  await page.screenshot({ path: ss("05-instructor-dashboard"), fullPage: true });

  // Navigate to org
  await page.goto(`/dashboard/orgs/${orgId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("06-org-overview"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 4: Create cohort
  // ═══════════════════════════════════════════
  await page.click("text=Cohorts");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.screenshot({ path: ss("07-cohorts-empty"), fullPage: true });

  await page.click("text=+ New Cohort");
  await page.fill('input[placeholder*="Cohort name"]', "AI 视觉商务 — 2026秋季");
  await page.fill('textarea[placeholder*="Description"]', "首期商业 AI 视觉创作培训班");
  await page.screenshot({ path: ss("08-cohort-form-filled"), fullPage: true });

  await page.click("button:has-text('Create Cohort')");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.screenshot({ path: ss("09-cohort-created"), fullPage: true });

  // Activate cohort via API
  const cohortList = await (await fetch(`${API}/orgs/${orgId}/cohorts`, {
    headers: adminAuth,
  })).json();
  const cohortId = cohortList.data[0].id;
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}`, {
    method: "PUT",
    headers: adminAuth,
    body: JSON.stringify({ status: "active" }),
  });

  // ═══════════════════════════════════════════
  // STEP 5: Click into cohort detail
  // ═══════════════════════════════════════════
  await page.click(`text=AI 视觉商务`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("10-cohort-detail"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 6: Add members to cohort
  // ═══════════════════════════════════════════
  // Add via API (browser needs user IDs)
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/members`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ user_id: instData.user.id, role: "instructor" }),
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/members`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ user_id: aliceData.user.id, role: "learner" }),
  });

  await page.click("text=Members");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("11-cohort-members"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 7: Create + assign skill
  // ═══════════════════════════════════════════
  const catRes = await (await fetch(`${API}/orgs/${orgId}/categories`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ name: "AI 创作" }),
  })).json();
  const skRes = await (await fetch(`${API}/orgs/${orgId}/skills`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ name: "Prompt 工程", description: "掌握 AI 提示词设计", difficulty: "intermediate", category_id: catRes.data.id }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/skills/${skRes.data.id}/publish`, {
    method: "POST", headers: adminAuth,
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/skills`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ skill_id: skRes.data.id }),
  });

  await page.click("text=Skills");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("12-cohort-skills"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 8: Create + assign project
  // ═══════════════════════════════════════════
  const projRes = await (await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({
      title: "AI 产品广告制作",
      description: "从客户简报到最终交付的完整 AI 广告制作流程",
      instructions: "按阶段完成每个交付物",
      rubric: [
        { criterion: "创意概念", max_score: 25 },
        { criterion: "视觉质量", max_score: 35 },
        { criterion: "商业可用性", max_score: 40 },
      ],
    }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${projRes.data.id}/publish`, {
    method: "POST", headers: adminAuth,
  });
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/projects`, {
    method: "POST",
    headers: adminAuth,
    body: JSON.stringify({ project_id: projRes.data.id }),
  });

  await page.click("text=Projects");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("13-cohort-projects"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 9: Check progress dashboard
  // ═══════════════════════════════════════════
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ss("14-cohort-progress-dashboard"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 10: Check progress drill-down
  // ═══════════════════════════════════════════
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("15-progress-list"), fullPage: true });

  // Click Alice
  if (await page.getByText("Alice Chen").isVisible()) {
    await page.click("text=Alice Chen");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: ss("16-alice-drilldown"), fullPage: true });
  }

  // ═══════════════════════════════════════════
  // STEP 11: Create client brief
  // ═══════════════════════════════════════════
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: ss("17-briefs-empty"), fullPage: true });

  await page.click("text=+ New Brief");
  await page.fill('input[placeholder*="Brief title"]', "Acme Q4 产品推广");
  await page.fill('input[placeholder*="Client name"]', "Acme 科技");
  await page.fill('textarea[placeholder*="Objective"]', "为 Q4 新品发布创建主视觉和社交媒体素材");
  await page.screenshot({ path: ss("18-brief-form"), fullPage: true });

  await page.click("button:has-text('Create Brief')");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.screenshot({ path: ss("19-brief-created"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 12: Brief detail
  // ═══════════════════════════════════════════
  await page.click("text=Acme Q4");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.screenshot({ path: ss("20-brief-detail"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 13: Convert brief to project
  // ═══════════════════════════════════════════
  await page.click("text=Convert to Project");
  await page.waitForTimeout(500);
  await page.screenshot({ path: ss("21-convert-form"), fullPage: true });

  await page.click("button:has-text('Create Project')");
  await page.waitForURL("**/projects/**", { timeout: 15000 });
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("22-converted-project"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 14: Login as Alice (learner)
  // ═══════════════════════════════════════════
  // Clear previous auth state
  await page.context().clearCookies();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByLabel('Email').fill(aliceEmail);
  await page.getByLabel('Password').fill(password);
  await page.getByRole("button", { name: /sign|log/i }).first().click();
  await page.waitForURL("**/dashboard**", { timeout: 10000 });

  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ss("23-alice-projects"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 15: Alice's my-dashboard
  // ═══════════════════════════════════════════
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("24-alice-my-dashboard"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 16: Login as Bob (not in cohort)
  // ═══════════════════════════════════════════
  // Clear previous auth state
  await page.context().clearCookies();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByLabel('Email').fill(bobEmail);
  await page.getByLabel('Password').fill(password);
  await page.getByRole("button", { name: /sign|log/i }).first().click();
  await page.waitForURL("**/dashboard**", { timeout: 10000 });

  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ss("25-bob-projects-no-cohort"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 17: Bob tries to access briefs (RBAC)
  // ═══════════════════════════════════════════
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("26-bob-briefs-forbidden"), fullPage: true });

  // ═══════════════════════════════════════════
  // STEP 18: Evaluation page
  // ═══════════════════════════════════════════
  // Clear previous auth state
  await page.context().clearCookies();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByLabel('Email').fill(instructorEmail);
  await page.getByLabel('Password').fill(password);
  await page.getByRole("button", { name: /sign|log/i }).first().click();
  await page.waitForURL("**/dashboard**", { timeout: 10000 });

  await page.goto(`/dashboard/orgs/${orgId}/evaluation`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ss("27-evaluation-page"), fullPage: true });

  // Done!
  console.log("✅ Manual user flow complete — 27 screenshots captured");
});
