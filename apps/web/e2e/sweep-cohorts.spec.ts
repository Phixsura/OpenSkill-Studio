/**
 * Sweep: COHORTS + CLIENT BRIEFS + OPPORTUNITIES browser E2E.
 *
 * Happy paths:
 * - create cohort via UI form (cohorts page inline form)
 * - enroll an org member into the cohort via the Members page select+Add
 * - assign a published project to the cohort via the Projects tab
 * - cohort overview dashboard renders member progress (stats + table)
 * - create client brief via UI form
 * - brief detail renders (objective, deliverables, status)
 * - convert brief → project via the "Convert to Project →" button
 * - admin reviews a student application via the Applications list (Accept)
 * - student sees brief-derived items on the Opportunities page
 *
 * Unhappy paths:
 * - student cannot create cohorts (403 → "Insufficient org permissions" toast)
 * - student cannot view the briefs admin list (403 → error message in UI)
 * - brief form validation (disabled submit + server-side objective length toast)
 * - empty states (cohorts, briefs, opportunities, cohort members, cohort projects)
 *
 * DOM anchors verified against page sources:
 * - cohorts/page.tsx: "+ New Cohort" button, placeholder "Cohort name (e.g. ...",
 *   "Create Cohort" button, empty state "No cohorts yet."
 * - cohorts/[cohortId]/page.tsx: h1 name, status badge, "Manage Members" /
 *   "Assign Projects" links, quick stats, "Project Progress" table
 * - cohorts/[cohortId]/members/page.tsx: two selects (member, role), "Add" button,
 *   empty state "No members enrolled yet."
 * - cohorts/[cohortId]/projects/page.tsx: one select, "Assign to Cohort" button,
 *   empty state "No projects assigned to this cohort yet."
 * - briefs/page.tsx: "+ New Brief", placeholders "Brief title" / "Client name" /
 *   "Objective — ...", "Create Brief" button, empty state "No client briefs yet."
 * - briefs/[briefId]/page.tsx: h1 title, "Objective" section, "Convert to Project →",
 *   "Create Project", Applications list with Accept/Reject buttons
 * - opportunities/page.tsx: h1 "Commercial Opportunities", "Open" badge, empty state
 *   "No open commercial projects at this time."
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, addOrgMember, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let student: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

const stamp = Date.now();
const cohortName = `Sweep Cohort ${stamp}`;
const briefTitle = `Sweep Brief ${stamp}`;
const openBriefTitle = `Open Opportunity ${stamp}`;
const projectTitle = `Sweep Project ${stamp}`;

let cohortUrl = "";
let briefUrl = "";
let openBriefId = "";

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function api(auth: AuthContext, method: string, path: string, body?: object) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: auth.headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return {};
  return res.json();
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("Sweep Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  student = await registerUser("Sweep Student");
  orgId = await createOrg(admin, `SweepCohorts-${stamp}`);
  await addOrgMember(admin, orgId, student.userId, "student");

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

test("admin: empty states, then create cohort via UI", async () => {
  // ── Empty states first (fresh org) ──
  await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
  await expect(page.getByText(/No cohorts yet/i)).toBeVisible({ timeout: 15_000 });

  await page.goto(`/dashboard/orgs/${orgId}/opportunities`);
  await expect(page.getByRole("heading", { name: "Commercial Opportunities" })).toBeVisible();
  await expect(page.getByText(/No open commercial projects/i)).toBeVisible({ timeout: 10_000 });

  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await expect(page.getByText(/No client briefs yet/i)).toBeVisible({ timeout: 10_000 });

  // ── Create cohort via the inline form ──
  await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
  await page.getByRole("button", { name: "+ New Cohort" }).click();
  await page.getByPlaceholder(/Cohort name/i).fill(cohortName);
  await page.getByPlaceholder("Description (optional)").fill("E2E sweep cohort");
  await page.getByRole("button", { name: "Create Cohort" }).click();

  // Card appears with name + draft badge + 0 members
  await expect(page.getByRole("heading", { name: cohortName })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("draft").first()).toBeVisible();
  await expect(page.getByText("0 members")).toBeVisible();
});

test("admin: cohort detail renders, enroll member via Members page UI", async () => {
  // Navigate into the cohort from the list card
  await page.getByRole("heading", { name: cohortName }).click();
  await page.waitForURL(/cohorts\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  cohortUrl = page.url();

  // Detail header + stats render
  await expect(page.getByRole("heading", { name: cohortName })).toBeVisible();
  await expect(page.getByText("E2E sweep cohort")).toBeVisible();
  await expect(page.getByRole("button", { name: "Activate Cohort" })).toBeVisible();
  await expect(page.getByText("No projects assigned to this cohort yet.")).toBeVisible({
    timeout: 10_000,
  });

  // ── Members page: empty state then add the student ──
  await page.getByRole("link", { name: "Manage Members" }).click();
  await page.waitForURL(/\/members$/, { timeout: 15_000 });
  await expect(page.getByText("No members enrolled yet.")).toBeVisible({ timeout: 10_000 });

  // First select = org member picker (value = user id), second = role
  await page.locator("select").first().selectOption(student.userId);
  await page.locator("select").nth(1).selectOption("learner");
  await page.getByRole("button", { name: "Add", exact: true }).click();

  // Enrolled row appears with the learner role badge
  const memberRow = page.locator("tbody tr", { hasText: "Sweep Student" });
  await expect(memberRow).toBeVisible({ timeout: 10_000 });
  await expect(memberRow.getByText("learner")).toBeVisible();
});

test("admin: assign published project via UI, dashboard shows member progress", async () => {
  // Seed a published project via API (heavy setup), assign through the UI
  const proj = await api(admin, "POST", `/orgs/${orgId}/projects`, {
    title: projectTitle,
    description: "Sweep project for cohort assignment",
    instructions: "Do the sweep work",
    rubric: [{ criterion: "Quality", max_score: 100 }],
  });
  const projectId = proj.data.id;
  await api(admin, "POST", `/orgs/${orgId}/projects/${projectId}/publish`);

  // ── Assign via the cohort Projects tab ──
  await page.goto(`${cohortUrl}/projects`);
  await expect(page.getByText("No projects assigned to this cohort yet.")).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByRole("heading", { name: "Assign Project" })).toBeVisible({
    timeout: 10_000,
  });
  await page.locator("select").selectOption(projectId);
  await page.getByRole("button", { name: "Assign to Cohort" }).click();

  // Assigned card renders with title + participation mode
  await expect(page.getByText(projectTitle)).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Mode: assigned")).toBeVisible();

  // ── Overview dashboard reflects member progress ──
  await page.goto(cohortUrl);
  await expect(page.getByText("Project Progress")).toBeVisible({ timeout: 15_000 });
  // Quick stats: 1 learner enrolled
  await expect(page.locator("div.rounded-lg.border", { hasText: /^1Learners$/ })).toBeVisible();
  // Progress table row: project title with 1 not-started learner
  const row = page.locator("tr", { hasText: projectTitle });
  await expect(row).toBeVisible();
  await expect(row.locator("td").nth(1)).toHaveText("1"); // Not Started

  // ── Progress tab lists the learner (two "Progress" links exist on the page:
  // the org sidebar and the cohort tab — pick the cohort-scoped one) ──
  await page.locator(`a[href="${new URL(cohortUrl).pathname}/progress"]`).click();
  await page.waitForURL(/\/progress$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Learner Progress" })).toBeVisible();
  await expect(page.getByText("Sweep Student")).toBeVisible({ timeout: 10_000 });
});

test("admin: brief form validation (unhappy), then create brief via UI", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await page.getByRole("button", { name: "+ New Brief" }).click();

  // Client-side gate: submit disabled until required fields are filled
  const createBtn = page.getByRole("button", { name: "Create Brief" });
  await expect(createBtn).toBeDisabled();

  // Server-side validation: objective shorter than 10 chars → 422 toast
  await page.getByPlaceholder("Brief title").fill(briefTitle);
  await page.getByPlaceholder("Client name").fill("ACME Studios");
  await page.locator("select").selectOption("social_media");
  await page.getByPlaceholder(/Objective/).fill("short");
  await expect(createBtn).toBeEnabled();
  await createBtn.click();
  await expect(page.getByText(/Objective must be at least 10 characters/i)).toBeVisible({
    timeout: 10_000,
  });
  // Form stayed open (creation failed)
  await expect(createBtn).toBeVisible();

  // Fix the objective and submit for real
  await page
    .getByPlaceholder(/Objective/)
    .fill("Produce a spring social media visual campaign for ACME.");
  await createBtn.click();

  // Brief appears in the list with client + type + draft badge
  await expect(page.getByRole("heading", { name: briefTitle })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("ACME Studios · social media")).toBeVisible();
  await expect(page.getByText("draft").first()).toBeVisible();
});

test("admin: brief detail renders, convert brief → project via UI", async () => {
  await page.getByRole("heading", { name: briefTitle }).click();
  await page.waitForURL(/briefs\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  briefUrl = page.url();

  // Detail renders
  await expect(page.getByRole("heading", { name: briefTitle })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Objective" })).toBeVisible();
  await expect(
    page.getByText("Produce a spring social media visual campaign for ACME."),
  ).toBeVisible();

  // ── Convert to project ──
  await page.getByRole("button", { name: /Convert to Project/ }).click();
  await expect(page.getByText(/create a new AI visual project/i)).toBeVisible();
  await page.getByRole("button", { name: "Create Project", exact: true }).click();

  // Redirects to the new project page which carries the brief title
  await page.waitForURL(/projects\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: briefTitle })).toBeVisible({ timeout: 10_000 });

  // Brief is now active and no longer convertible
  await page.goto(briefUrl);
  await expect(page.getByText("active").first()).toBeVisible({ timeout: 10_000 });
  await expect(page.getByRole("button", { name: /Convert to Project/ })).toHaveCount(0);
});

test("admin: reviews a student application via the Applications list", async () => {
  // Seed: an OPEN brief + a student application (both via API — status "open"
  // has no UI control, and the student-side apply UI is bug-blocked, see fixme)
  const brief = await api(admin, "POST", `/orgs/${orgId}/briefs`, {
    title: openBriefTitle,
    client_name: "Northwind Co",
    project_type: "product_visualization",
    objective: "Product hero shots for the catalog relaunch.",
  });
  openBriefId = brief.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/briefs/${openBriefId}`, { status: "open" });
  await api(student, "POST", `/orgs/${orgId}/briefs/${openBriefId}/apply`, {
    note: "I would love to shoot this catalog.",
  });

  // ── Admin sees and accepts the application in the UI ──
  await page.goto(`/dashboard/orgs/${orgId}/briefs/${openBriefId}`);
  await expect(page.getByRole("heading", { name: openBriefTitle })).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByText("Applications (1)")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Sweep Student")).toBeVisible();
  await expect(page.getByText("I would love to shoot this catalog.")).toBeVisible();

  await page.getByRole("button", { name: "Accept", exact: true }).click();
  await expect(page.getByText("accepted").first()).toBeVisible({ timeout: 10_000 });
  await expect(page.getByRole("button", { name: "Accept", exact: true })).toHaveCount(0);
});

test("student: cannot create cohorts — 403 toast in UI", async () => {
  await loginInBrowser(page, student.email, "TestPass123!");

  // The "+ New Cohort" control is NOT role-hidden; the API rejects with 403
  await page.goto(`/dashboard/orgs/${orgId}/cohorts`);
  await expect(page.getByRole("heading", { name: "Cohorts" })).toBeVisible({ timeout: 15_000 });
  await page.getByRole("button", { name: "+ New Cohort" }).click();
  await page.getByPlaceholder(/Cohort name/i).fill("Student Rogue Cohort");
  await page.getByRole("button", { name: "Create Cohort" }).click();

  // Error toast surfaces the permission failure
  await expect(page.getByText("Insufficient org permissions")).toBeVisible({ timeout: 10_000 });
  // No card was created for it
  await expect(page.getByRole("heading", { name: "Student Rogue Cohort" })).toHaveCount(0);
});

test("student: briefs admin list is permission-blocked (error state in UI)", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/briefs`);
  await expect(page.getByText(/Failed to load briefs/i)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/No client briefs yet/i)).toHaveCount(0);
});

test("student: opportunities page renders brief-derived items", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/opportunities`);
  await expect(page.getByRole("heading", { name: "Commercial Opportunities" })).toBeVisible({
    timeout: 15_000,
  });
  // The open brief shows as an opportunity card
  const card = page.locator("a", { hasText: openBriefTitle });
  await expect(card).toBeVisible({ timeout: 10_000 });
  await expect(card.getByText("Northwind Co · Product Visualization")).toBeVisible();
  await expect(card.getByText("Open", { exact: true })).toBeVisible();
  await expect(card.getByText("Product hero shots for the catalog relaunch.")).toBeVisible();
});

/**
 * APP BUG: students cannot apply to opportunities through the UI.
 *
 * Repro: as a student org member, open /dashboard/orgs/{orgId}/opportunities and
 * click any open opportunity card. It links to /dashboard/orgs/{orgId}/briefs/{id},
 * but GET /api/v1/orgs/{org_id}/briefs/{brief_id} requires INSTRUCTOR_ROLES
 * (apps/api/app/api/v1/endpoints/client_briefs.py, get_brief), so the page shows
 * "Failed to load brief. It may not exist or you don't have access." The Apply
 * textarea + button live on that page, making them unreachable — even though
 * POST /briefs/{id}/apply itself allows any org member (and works via API).
 * Fix: allow members to GET open/active briefs, or give opportunities its own
 * student-facing detail/apply view.
 */
test("student: opportunity card opens the brief detail with application state", async () => {
  // Fixed: get_brief now allows plain members to view OPEN briefs, and
  // list_applications returns the member's own application — so the page
  // renders the "you have applied" state (this student applied via API in
  // the earlier admin-review test).
  await page.goto(`/dashboard/orgs/${orgId}/opportunities`);
  await page.locator("a", { hasText: openBriefTitle }).click();
  await page.waitForURL(/briefs\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: openBriefTitle })).toBeVisible();
  await expect(page.getByText(/You have applied/)).toBeVisible({ timeout: 10_000 });

  // A SECOND student (never applied) sees the Apply form and can submit it
  const student2 = await registerUser("Sweep Student 2");
  await addOrgMember(admin, orgId, student2.userId, "student");
  const ctx2 = await page.context().browser()!.newContext();
  const page2 = await ctx2.newPage();
  await loginInBrowser(page2, student2.email, "TestPass123!");
  await page2.goto(page.url());
  await expect(page2.getByRole("heading", { name: openBriefTitle })).toBeVisible();
  await page2.getByPlaceholder(/Why do you want to work on this/).fill("Pick me!");
  await page2.getByRole("button", { name: "Apply", exact: true }).click();
  await expect(page2.getByText(/You have applied/)).toBeVisible({ timeout: 10_000 });
  // Privacy: the student sees only their OWN application, not the other's
  await expect(page2.getByText("Applications (1)")).toBeVisible();
  await ctx2.close();
});
