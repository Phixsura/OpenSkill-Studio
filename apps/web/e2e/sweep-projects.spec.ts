/**
 * Sweep: PROJECTS + SUBMISSIONS + REVIEWS + EVALUATION SETTINGS.
 *
 * Flow: instructor creates a project via the UI form (rubric criteria added
 * and removed through the rubric textarea — the form's one-criterion-per-line
 * editor), publishes (via API — see APP BUG note below: the web UI exposes no
 * publish control for projects), a student submits a text deliverable through
 * the UI, the instructor reviews it (UI score validation + approve), and the
 * student sees the final score in the UI. Plus unhappy paths: draft project
 * hidden from students (404 + empty list), student blocked from the reviews
 * dashboard, project-form validation error surfaced from the API, review
 * score UI validation, and evaluation-settings persistence.
 *
 * DOM anchors (verified against page sources):
 * - projects/new:      #title #description #instructions #maxScore #rubric,
 *                      "Create Project" button, error div renders ApiError text
 * - projects/[id]:     h1 title, Rubric table (Criterion/Max Score),
 *                      "New Submission" link-button, submission rows
 *                      "v{n} — {status}" + "{final_score}/{max_score}",
 *                      "Failed to load project." on 404
 * - projects/[id]/submit: "Start Draft" button, textarea placeholder
 *                      "Enter {deliverable}...", "Submit" button
 * - reviews:           "Pending Reviews" h1, "No pending reviews" empty state,
 *                      "Review →" row link, "Failed to load reviews." on error
 * - reviews/[subId]:   score input placeholder "0-100" (hardcoded max 100),
 *                      feedback textarea, "✅ Approve" button,
 *                      client-side error "Score must be between 0 and 100"
 * - evaluation/settings: threshold = input[type=number][max="1"],
 *                      "Save Settings" button, "Settings saved." message
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, addOrgMember, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let student: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;
let projectId: string;

const PROJECT_TITLE = `Sweep Chatbot ${Date.now()}`;

async function api(auth: AuthContext, method: string, path: string, body?: object) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: auth.headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.json();
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  admin = await registerUser("Sweep Instructor");
  orgId = await createOrg(admin, `SweepProj-${Date.now()}`);
  student = await registerUser("Sweep Student");
  await addOrgMember(admin, orgId, student.userId, "student");

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

// ── Happy: create project via UI form with rubric add/remove ──────────────

test("instructor creates project via UI form, adding then removing a rubric criterion", async () => {
  test.setTimeout(90_000);

  await page.goto(`/dashboard/orgs/${orgId}/projects/new`);
  await page.waitForLoadState("networkidle");

  await page.locator("#title").fill(PROJECT_TITLE);
  await page.locator("#description").fill("Build an AI chatbot end to end.");
  await page
    .locator("#instructions")
    .fill("## Requirements\n\n1. Build a chatbot\n2. Write a reflection");
  await page.locator("#maxScore").fill("100");

  // The rubric editor is one-criterion-per-line. Add 4 criteria...
  await page
    .locator("#rubric")
    .fill("Functionality: 40\nCode Quality: 30\nInnovation: 20\nExtra Credit: 10");
  // ...then REMOVE the "Extra Credit" criterion (delete its line).
  await page.locator("#rubric").fill("Functionality: 40\nCode Quality: 30\nInnovation: 30");

  await page.getByRole("button", { name: "Create Project" }).click();

  await page.waitForURL(/projects\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  projectId = page.url().split("/").pop()!;

  await expect(page.getByRole("heading", { name: PROJECT_TITLE })).toBeVisible();

  // Rubric table reflects the final criteria — including the removed one being gone
  await expect(page.getByRole("cell", { name: "Functionality" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Code Quality" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Innovation" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Extra Credit" })).toHaveCount(0);
  await expect(page.getByRole("cell", { name: "40", exact: true })).toBeVisible();
});

// ── Unhappy: project form surfaces API validation error in the UI ─────────

test("project form shows API validation error for invalid max score", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/projects/new`);
  await page.waitForLoadState("networkidle");

  await page.locator("#title").fill("Invalid Project");
  await page.locator("#description").fill("desc");
  await page.locator("#instructions").fill("instr");
  await page.locator("#maxScore").fill("-5");
  await page.locator("#rubric").fill("Quality: 100");
  await page.getByRole("button", { name: "Create Project" }).click();

  // API 422 → error banner with the validation message; stays on the form
  await expect(page.getByText(/Max score must be between 1 and 10,000/)).toBeVisible({
    timeout: 10_000,
  });
  await expect(page).toHaveURL(/projects\/new$/);
});

// ── Evaluation settings: renders + pass_threshold change persists ──────────
// (Runs while the admin from beforeAll is still logged in — serial mode.)

test("evaluation settings page renders and saving a new pass threshold persists it", async () => {
  test.setTimeout(90_000);

  await page.goto(`/dashboard/orgs/${orgId}/evaluation/settings`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: "AI Evaluation Settings" })).toBeVisible();
  await expect(page.getByText("Pass Threshold")).toBeVisible();

  // The threshold field is the only number input capped at 1
  const threshold = page.locator('input[type="number"][max="1"]');
  await expect(threshold).toBeVisible();
  await threshold.fill("0.85");
  await page.getByRole("button", { name: "Save Settings" }).click();
  await expect(page.getByText("Settings saved.")).toBeVisible({ timeout: 10_000 });

  // Persistence: the backend really stored the new threshold
  const settings = await api(admin, "GET", `/orgs/${orgId}/settings/evaluation`);
  expect(settings.data.pass_threshold).toBe(0.85);
});

// APP BUG: the evaluation settings page never displays persisted values. The
// GET /orgs/{org_id}/settings/evaluation endpoint returns the standard
// { data: {...} } envelope (DataResponse[EvalSettingsResponse]), but
// evaluation/settings/page.tsx calls apiWithAuth<EvalSettings>(...) and reads
// settings.enabled / settings.pass_threshold etc. directly off the ENVELOPE,
// so every field is undefined and the form falls back to defaults ("0.6")
// after every reload, even though the backend holds the saved value.
// Verified live: API returns pass_threshold 0.85 / enabled true, reloaded UI
// shows "0.6" and an unchecked box.
// Suspected file: apps/web/src/app/(dashboard)/dashboard/orgs/[orgId]/evaluation/settings/page.tsx
// (missing .data unwrap in the useQuery queryFn / useEffect sync).
test("reloaded evaluation settings page shows the persisted pass threshold", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/evaluation/settings`);
  await page.waitForLoadState("networkidle");
  const threshold = page.locator('input[type="number"][max="1"]');
  await expect(threshold).toHaveValue("0.85");
});

// ── Unhappy: student cannot see a draft (unpublished) project ──────────────

test("student sees empty project list and 404 page for a draft project", async () => {
  test.setTimeout(90_000);
  await loginInBrowser(page, student.email, "TestPass123!");

  // List: the draft project must not appear — empty state instead
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("No projects yet.")).toBeVisible();
  await expect(page.getByText(PROJECT_TITLE)).toHaveCount(0);

  // Direct deep-link: API returns 404, UI shows the failure state
  await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Failed to load project.")).toBeVisible();
  await expect(page.getByRole("heading", { name: PROJECT_TITLE })).toHaveCount(0);
});

// ── Unhappy: student is denied the reviews dashboard ───────────────────────

test("student gets permission-denied error state on reviews dashboard", async () => {
  // Still logged in as student (serial mode)
  await page.goto(`/dashboard/orgs/${orgId}/reviews`);
  await page.waitForLoadState("networkidle");
  // /reviews/pending requires an instructor role → 403 → error state in UI
  await expect(page.getByText(/Failed to load reviews/)).toBeVisible();
  await expect(page.getByText(/Review →/)).toHaveCount(0);
});

// ── Happy: publish → student submits a text deliverable via the UI ─────────
//
// NOTE (APP BUG, documented in report): the web UI exposes NO publish control
// for projects anywhere — POST /projects/{id}/publish exists in the API but no
// page or button calls it. Publishing here is done via API to unblock the flow.

test("student opens published project, starts draft, adds text item, submits", async () => {
  test.setTimeout(90_000);

  // Seed via API: a required text deliverable + publish (no UI for either;
  // deliverables have no UI editor and publish has no UI button)
  const deliv = await api(admin, "POST", `/orgs/${orgId}/projects/${projectId}/deliverables`, {
    name: "Reflection",
    type: "text",
    required: true,
  });
  expect(deliv.data?.id).toBeTruthy();
  const pub = await api(admin, "POST", `/orgs/${orgId}/projects/${projectId}/publish`, {});
  expect(pub.data?.status).toBe("published");

  // Student (still logged in) now sees the project in the list
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(PROJECT_TITLE)).toBeVisible();
  await page.getByText(PROJECT_TITLE).click();
  await page.waitForURL(new RegExp(`projects/${projectId}$`), { timeout: 15_000 });

  // Project detail renders instructions + rubric for the student
  await expect(page.getByRole("heading", { name: PROJECT_TITLE })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Functionality" })).toBeVisible();

  // New Submission → Start Draft → fill the text deliverable → Submit
  await page.getByRole("link", { name: "New Submission" }).click();
  await page.waitForURL(/\/submit$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("What you'll submit")).toBeVisible();
  await expect(page.getByText("Reflection")).toBeVisible();

  await page.getByRole("button", { name: "Start Draft" }).click();
  const textarea = page.getByPlaceholder("Enter Reflection...");
  await expect(textarea).toBeVisible({ timeout: 10_000 });
  await textarea.fill("My reflection: I built a retrieval-augmented chatbot and learned a lot.");
  await page.getByRole("button", { name: "Submit", exact: true }).click();

  // Redirects back to the project detail; the submission row shows as submitted
  await page.waitForURL(new RegExp(`projects/${projectId}$`), { timeout: 15_000 });
  await expect(page.getByText("My Submissions")).toBeVisible();
  await expect(page.getByText(/v1 —/)).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("submitted", { exact: true })).toBeVisible();
});

// ── Happy + unhappy: instructor reviews (UI validation, then approve) ──────

test("instructor sees pending review, UI rejects out-of-range score, then approves", async () => {
  test.setTimeout(90_000);
  await loginInBrowser(page, admin.email, "TestPass123!");

  await page.goto(`/dashboard/orgs/${orgId}/reviews`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("1 submission awaiting review.")).toBeVisible();
  await expect(page.getByRole("cell", { name: "Sweep Student", exact: false })).toBeVisible();
  await expect(page.getByRole("cell", { name: PROJECT_TITLE })).toBeVisible();

  await page.getByRole("link", { name: "Review →" }).click();
  await page.waitForURL(/reviews\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");

  // The student's submitted text item is visible to the reviewer
  await expect(page.getByText(/retrieval-augmented chatbot/)).toBeVisible({ timeout: 10_000 });

  // UNHAPPY: score above max → client-side validation error, no submit
  const scoreInput = page.getByPlaceholder("0-100");
  await scoreInput.fill("150");
  await page.getByRole("button", { name: /Approve/ }).click();
  await expect(page.getByText("Score must be between 0 and 100")).toBeVisible();
  // Still on the review page — the invalid review was not submitted
  await expect(page).toHaveURL(/reviews\/[0-9A-Z]{26}$/);

  // HAPPY: valid score + feedback → approve → back to (now empty) queue
  await scoreInput.fill("85");
  await page
    .getByPlaceholder("Provide constructive feedback...")
    .fill("Solid work — clear reflection and good structure.");
  await page.getByRole("button", { name: /Approve/ }).click();
  await page.waitForURL(/\/reviews$/, { timeout: 15_000 });
  await expect(page.getByText(/No pending reviews/)).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("0 submissions awaiting review.")).toBeVisible();
});

// ── Happy: student sees the score in the UI ────────────────────────────────

test("student sees the approved status and final score on the project page", async () => {
  test.setTimeout(90_000);
  await loginInBrowser(page, student.email, "TestPass123!");

  await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}`);
  await page.waitForLoadState("networkidle");

  await expect(page.getByText("My Submissions")).toBeVisible();
  await expect(page.getByText("approved", { exact: true })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("85/100")).toBeVisible();
});
