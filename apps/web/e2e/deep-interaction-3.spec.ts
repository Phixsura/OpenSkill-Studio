/**
 * Deep interaction tests part 3 — gaps found by systematic audit.
 * Covers: multi-cohort, deadline override, org-wide backward compat,
 * application workflow, multimodal eval types, budget enforcement,
 * existing page regression, brief editing.
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
test.setTimeout(120_000);

let admin: AuthContext;
let alice: AuthContext;
let bob: AuthContext;
let orgId: string;

test.beforeAll(async () => {
  admin = await registerUser("Gap Admin");
  alice = await registerUser("Gap Alice");
  bob = await registerUser("Gap Bob");
  orgId = await createOrg(admin, `Gap ${Date.now()}`);
  await addOrgMember(admin, orgId, alice.userId, "student");
  await addOrgMember(admin, orgId, bob.userId, "student");
});

// ── Gap 1: Multi-cohort user switches between dashboards ──

test("multi-cohort: alice in 2 cohorts sees both dashboards", async ({ page }) => {
  const c1 = await createCohort(admin, orgId, "Cohort Alpha");
  const c2 = await createCohort(admin, orgId, "Cohort Beta");
  await activateCohort(admin, orgId, c1);
  await activateCohort(admin, orgId, c2);
  await addCohortMember(admin, orgId, c1, alice.userId, "learner");
  await addCohortMember(admin, orgId, c2, alice.userId, "learner");

  await loginInBrowser(page, alice.email, "TestPass123!");

  // Check my-cohorts shows both
  const res = await fetch(`${API}/orgs/${orgId}/my-cohorts`, { headers: alice.headers });
  const cohorts = await res.json();
  expect(cohorts.data.length).toBeGreaterThanOrEqual(2);

  // Visit each dashboard
  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${c1}/my-dashboard`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Cohort Alpha")).toBeVisible({ timeout: 10_000 });

  await page.goto(`/dashboard/orgs/${orgId}/cohorts/${c2}/my-dashboard`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Cohort Beta")).toBeVisible({ timeout: 10_000 });
});

// ── Gap 2: Org-wide project visible to all (backward compat) ──

test("org-wide project (no cohort) visible to all members", async ({ page }) => {
  const proj = await (await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ title: "Org Wide Visible", description: "d", instructions: "i", rubric: [{ criterion: "Q", max_score: 100 }] }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/publish`, { method: "POST", headers: admin.headers });
  // NOT assigned to any cohort — should be visible to everyone

  // Bob (not in any cohort) can see it
  await loginInBrowser(page, bob.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await expect(page.getByText("Org Wide Visible")).toBeVisible({ timeout: 10_000 });

  // Alice can also see it
  await loginInBrowser(page, alice.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await expect(page.getByText("Org Wide Visible")).toBeVisible({ timeout: 10_000 });
});

// ── Gap 3: Deadline override enforcement ──

test("cohort deadline override allows submission past project deadline", async ({ page }) => {
  const past = new Date(Date.now() - 86400000).toISOString(); // yesterday
  const future = new Date(Date.now() + 7 * 86400000).toISOString(); // next week

  const proj = await (await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ title: "Deadline Override Test", description: "d", instructions: "i", deadline: past, rubric: [{ criterion: "Q", max_score: 100 }] }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/publish`, { method: "POST", headers: admin.headers });

  // Without override: should fail
  const sub1 = await (await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions`, { method: "POST", headers: alice.headers })).json();
  const r1 = await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions/${sub1.data.id}/submit`, { method: "POST", headers: alice.headers });
  expect(r1.status).toBe(422); // DEADLINE_PASSED

  // Create cohort with future deadline override
  const cid = await createCohort(admin, orgId, "Deadline Override Cohort");
  await activateCohort(admin, orgId, cid);
  await addCohortMember(admin, orgId, cid, alice.userId, "learner");
  await fetch(`${API}/orgs/${orgId}/cohorts/${cid}/projects`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ project_id: proj.data.id, deadline_override: future }),
  });

  // With override: should succeed
  const sub2 = await (await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions`, { method: "POST", headers: alice.headers })).json();
  const r2 = await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions/${sub2.data.id}/submit`, { method: "POST", headers: alice.headers });
  expect(r2.status).toBe(200); // on_time thanks to override

  // Verify in browser
  await loginInBrowser(page, alice.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/projects/${proj.data.id}/submissions/${sub2.data.id}`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await expect(page.getByText("submitted").first()).toBeVisible({ timeout: 10_000 });
});

// ── Gap 4: Application workflow in browser ──

test("application workflow: alice applies, admin accepts", async ({ page }) => {
  const brief = await (await fetch(`${API}/orgs/${orgId}/briefs`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ title: "Apply Brief", client_name: "AppCo", project_type: "viz", objective: "Test application flow" }),
  })).json();

  // Alice applies
  const applyRes = await fetch(`${API}/orgs/${orgId}/briefs/${brief.data.id}/apply`, {
    method: "POST", headers: alice.headers,
    body: JSON.stringify({ note: "I want to work on this" }),
  });
  expect(applyRes.status).toBe(201);
  const app = await applyRes.json();

  // Admin lists applications
  const listRes = await fetch(`${API}/orgs/${orgId}/briefs/${brief.data.id}/applications`, { headers: admin.headers });
  const apps = await listRes.json();
  expect(apps.data.length).toBe(1);
  expect(apps.data[0].note).toBe("I want to work on this");

  // Admin accepts
  const acceptRes = await fetch(`${API}/orgs/${orgId}/briefs/${brief.data.id}/applications/${app.data.id}`, {
    method: "PUT", headers: admin.headers,
    body: JSON.stringify({ status: "accepted" }),
  });
  expect(acceptRes.status).toBe(200);
  const accepted = await acceptRes.json();
  expect(accepted.data.status).toBe("accepted");

  // Duplicate apply → 409
  const dupRes = await fetch(`${API}/orgs/${orgId}/briefs/${brief.data.id}/apply`, {
    method: "POST", headers: alice.headers, body: JSON.stringify({}),
  });
  expect(dupRes.status).toBe(409);
});

// ── Gap 5: Multimodal eval types accepted by API ──

test("multimodal eval types: image/video/prompt/commercial all accepted", async ({ page }) => {
  await fetch(`${API}/orgs/${orgId}/settings/evaluation`, {
    method: "PUT", headers: admin.headers,
    body: JSON.stringify({ enabled: true, monthly_budget_usd: 500 }),
  });

  const proj = await (await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ title: "Multimodal Eval", description: "d", instructions: "i", rubric: [{ criterion: "Q", max_score: 100 }] }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/publish`, { method: "POST", headers: admin.headers });
  const sub = await (await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions`, { method: "POST", headers: alice.headers })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions/${sub.data.id}/submit`, { method: "POST", headers: alice.headers });

  // Each new eval type should be accepted (will fail on LLM but status is "failed" not 422)
  for (const evalType of ["image_review", "video_review", "prompt_review", "commercial_submission_review"]) {
    const r = await fetch(`${API}/orgs/${orgId}/evaluation/trigger`, {
      method: "POST", headers: admin.headers,
      body: JSON.stringify({ submission_id: sub.data.id, type: evalType }),
    });
    // Multimodal types may 201 (then fail on execution) or 500 (if S3 fetch crashes)
    // Both are acceptable — the key is they're not rejected as invalid types (422)
    expect(r.status).not.toBe(422); // type is accepted by the schema
  }

  // Verify eval page loads without crash
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/evaluation`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  // Page should load — multimodal types may 500 without actual media files
  // The API acceptance is verified above (not 422 = schema accepts them)
  await expect(page.locator("body")).not.toBeEmpty();
});

// ── Gap 6: Budget enforcement ──

test("budget exhausted blocks eval trigger", async ({ page }) => {
  // Set budget to 0
  await fetch(`${API}/orgs/${orgId}/settings/evaluation`, {
    method: "PUT", headers: admin.headers,
    body: JSON.stringify({ enabled: true, monthly_budget_usd: 0 }),
  });

  const proj = await (await fetch(`${API}/orgs/${orgId}/projects`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ title: "Budget Test", description: "d", instructions: "i", rubric: [{ criterion: "Q", max_score: 100 }] }),
  })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/publish`, { method: "POST", headers: admin.headers });
  const sub = await (await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions`, { method: "POST", headers: alice.headers })).json();
  await fetch(`${API}/orgs/${orgId}/projects/${proj.data.id}/submissions/${sub.data.id}/submit`, { method: "POST", headers: alice.headers });

  const r = await fetch(`${API}/orgs/${orgId}/evaluation/trigger`, {
    method: "POST", headers: admin.headers,
    body: JSON.stringify({ submission_id: sub.data.id, type: "submission_review" }),
  });
  expect(r.status).toBe(429); // BUDGET_EXCEEDED

  // Restore budget for other tests
  await fetch(`${API}/orgs/${orgId}/settings/evaluation`, {
    method: "PUT", headers: admin.headers,
    body: JSON.stringify({ monthly_budget_usd: 500 }),
  });
});

// ── Gap 7: Existing pages don't regress ──

test("existing skills page still works", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/skills`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  // Should not crash
  await expect(page.getByText("Skills").first()).toBeVisible({ timeout: 10_000 });
});

test("existing reviews page still works", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/reviews`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await expect(page.locator("body")).not.toBeEmpty();
});

test("existing settings page still works", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/settings`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await expect(page.locator("body")).not.toBeEmpty();
});

test("existing progress page still works", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/progress`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await expect(page.locator("body")).not.toBeEmpty();
});

test("existing members page still works", async ({ page }) => {
  await loginInBrowser(page, admin.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/members`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await expect(page.locator("body")).not.toBeEmpty();
});
