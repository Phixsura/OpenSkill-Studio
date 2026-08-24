/**
 * Sweep: SKILLS + CATEGORIES + LEARNING PATHS + PROGRESS browser E2E.
 *
 * Pages exercised (all under /dashboard/orgs/[orgId]/):
 * - skills            (list, search box, difficulty filter, empty state)
 * - skills/new        (create form, server validation error banner)
 * - skills/[skillId]  (detail, exercises list, sidebar)
 * - skills/[skillId]/exercises/[exerciseId] (MCQ attempt: validation,
 *   incorrect feedback, correct feedback)
 * - paths             (list, empty state)
 * - paths/new         (create form)
 * - paths/[pathId]    (add skill item, publish, status badge)
 * - progress          (stat cards + progress bar)
 *
 * DOM anchors (verified against page sources):
 * - skills/new: #name, #description, #category, #difficulty, #tags,
 *   #minutes, #learningContent, "Create Skill" button, error div text
 * - skills list: Input placeholder "Search skills...", unlabeled difficulty
 *   <select> (only select on page when no cohorts), "No skills found."
 * - exercise page: option <label>s, "Submit" button,
 *   "Please select an answer.", "✅ Correct! — X/Y pts", "❌ Incorrect — X/Y pts"
 * - paths/new: #name, #description, #estimated_minutes, "Create Learning Path"
 * - path detail: #add-item-type, #add-item-skill, "Add Item", "Publish",
 *   status badge span, "No items yet..." empty state
 * - progress: StatCards "Skills Completed", "Exercises Done", "Completion"
 *
 * UI coverage gaps found while reading sources (NOT app bugs, documented):
 * - No UI to create a category (skills/new explicitly says "Create a category
 *   first via the API") → seeded via API, dropdown population asserted.
 * - No UI button to publish a skill (API POST /skills/{id}/publish exists)
 *   → published via API, list/detail visibility asserted in UI.
 * - No UI form to add an exercise → seeded via API, rendering asserted.
 * - Skill description has NO server-side min length (only max 10,000), so a
 *   "too-short description" cannot produce a server error; the empty case is
 *   blocked by native `required`, and the server validation banner is
 *   exercised via the name field (2-200 chars) instead.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, addOrgMember, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let student: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

let categoryId: string;
let publishedSkillId: string; // created through the UI, then published via API
let draftSkillId: string; // seeded via API, stays draft
let exerciseId: string;

const RUN = Date.now();
const CATEGORY_NAME = `Sweep Category ${RUN}`;
const SKILL_NAME = `Sweep Prompting Basics ${RUN}`;
const DRAFT_SKILL_NAME = `Sweep Draft Advanced ${RUN}`;
const PATH_NAME = `Sweep Path ${RUN}`;

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
  admin = await registerUser("Sweep Skills Admin");
  orgId = await createOrg(admin, `SweepSkills-${RUN}`);

  student = await registerUser("Sweep Skills Student");
  await addOrgMember(admin, orgId, student.userId, "student");

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

// ── 1. Empty states (unhappy path) ─────────────────────────

test("empty states: no skills and no paths in a fresh org", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/skills`);
  await expect(page.getByRole("heading", { name: "Skills" })).toBeVisible();
  await expect(page.getByText("No skills found.")).toBeVisible({ timeout: 15_000 });

  await page.goto(`/dashboard/orgs/${orgId}/paths`);
  await expect(page.getByRole("heading", { name: "Learning Paths" })).toBeVisible();
  await expect(page.getByText("No learning paths yet.")).toBeVisible({ timeout: 15_000 });
});

// ── 2. Category (no creation UI exists — seed via API, assert dropdown) ──

test("category seeded via API populates the new-skill form dropdown", async () => {
  // The new-skill page has no category-creation UI: it instructs
  // "Create a category first via the API or ask an admin."
  // First verify that guidance renders when the org has zero categories.
  await page.goto(`/dashboard/orgs/${orgId}/skills/new`);
  await expect(page.getByText(/No categories yet/i)).toBeVisible({ timeout: 15_000 });

  const res = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: CATEGORY_NAME,
    description: "Category seeded by the sweep-skills E2E",
  });
  expect(res.data?.id).toBeTruthy();
  categoryId = res.data.id;

  // Reload — the dropdown must now offer the category.
  await page.reload();
  const categorySelect = page.locator("#category");
  await expect(categorySelect).toBeVisible({ timeout: 15_000 });
  await expect(categorySelect.locator("option", { hasText: CATEGORY_NAME })).toHaveCount(1);
});

// ── 3. Create skill via UI: server validation error, then success ──

test("new skill form: server validation error shown, then successful create", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/skills/new`);
  await expect(page.locator("#category")).toBeVisible({ timeout: 15_000 });

  // Unhappy: empty description is blocked client-side by native `required` —
  // submitting must keep us on the form (no navigation, no error banner).
  await page.locator("#name").fill(SKILL_NAME);
  await page.locator("#category").selectOption(categoryId);
  await page.getByRole("button", { name: "Create Skill" }).click();
  await expect(page).toHaveURL(new RegExp(`/orgs/${orgId}/skills/new$`));

  // Unhappy: 1-char name trips the server's 2-200 char rule (the description
  // field has no server-side min length — see file header) and the API error
  // message must surface in the red banner.
  await page.locator("#name").fill("X");
  await page.locator("#description").fill("short"); // passes: no min length server-side
  await page.getByRole("button", { name: "Create Skill" }).click();
  await expect(page.getByText(/Name must be 2-200 characters/)).toBeVisible({
    timeout: 10_000,
  });
  await expect(page).toHaveURL(new RegExp(`/orgs/${orgId}/skills/new$`));

  // Happy: valid form → redirect to the skill detail page.
  await page.locator("#name").fill(SKILL_NAME);
  await page.locator("#description").fill("Learn the fundamentals of prompting LLMs effectively.");
  await page.locator("#difficulty").selectOption("beginner");
  await page.locator("#tags").fill("ai, prompting");
  await page.locator("#minutes").fill("30");
  await page.locator("#learningContent").fill("# Intro\n\nPrompting 101 content.");
  await page.getByRole("button", { name: "Create Skill" }).click();

  await page.waitForURL(/\/skills\/[0-9A-HJKMNP-TV-Z]{26}$/, { timeout: 15_000 });
  publishedSkillId = page.url().split("/").pop()!;
  await expect(page.getByRole("heading", { name: SKILL_NAME })).toBeVisible();
  await expect(
    page.getByText("Learn the fundamentals of prompting LLMs effectively."),
  ).toBeVisible();
  // Sidebar details + tags render
  await expect(page.getByText("Est. time")).toBeVisible();
  await expect(page.getByText("30 min")).toBeVisible();
  await expect(page.getByText("prompting", { exact: true })).toBeVisible();
});

// ── 4. Skill list: search + difficulty filter + no-results state ──

test("skills list: search and difficulty filter narrow results", async () => {
  // Seed a second, advanced, draft skill via API for filter contrast.
  const res = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: DRAFT_SKILL_NAME,
    description: "Advanced draft skill for filter testing.",
    category_id: categoryId,
    difficulty: "advanced",
  });
  expect(res.data?.id).toBeTruthy();
  draftSkillId = res.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/skills`);
  // Admin sees both (drafts included for instructor roles).
  await expect(page.getByText(SKILL_NAME)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(DRAFT_SKILL_NAME)).toBeVisible();

  // Search narrows to one card.
  await page.getByPlaceholder("Search skills...").fill("Prompting Basics");
  await expect(page.getByText(DRAFT_SKILL_NAME)).not.toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(SKILL_NAME)).toBeVisible();
  await page.getByPlaceholder("Search skills...").fill("");

  // Difficulty filter (the only <select> on this page when no cohorts exist).
  const difficultySelect = page.locator("select").first();
  await difficultySelect.selectOption("advanced");
  await expect(page.getByText(SKILL_NAME)).not.toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(DRAFT_SKILL_NAME)).toBeVisible();

  // Unhappy: a difficulty with no matches shows the empty state.
  await difficultySelect.selectOption("expert");
  await expect(page.getByText("No skills found.")).toBeVisible({ timeout: 10_000 });
  await difficultySelect.selectOption("");
});

// ── 5. Publish (API — no UI button) + exercise seeding + detail rendering ──

test("published skill detail renders API-seeded MCQ exercise", async () => {
  // No publish button exists in the skill UI — publish via API.
  const pub = await api(admin, "POST", `/orgs/${orgId}/skills/${publishedSkillId}/publish`);
  expect(pub.data?.status).toBe("published");

  // No add-exercise UI form exists — seed the MCQ via API.
  const ex = await api(admin, "POST", `/orgs/${orgId}/skills/${publishedSkillId}/exercises`, {
    title: "Pick the best prompt",
    description: "Choose the prompt most likely to produce a structured answer.",
    type: "multiple_choice",
    config: {
      options: [
        { id: "a", text: "Return the answer as JSON with keys name and age" },
        { id: "b", text: "Tell me stuff" },
      ],
      correct: ["a"],
      multiple: false,
      explanation: "Explicit structure instructions win.",
    },
    max_score: 100,
  });
  expect(ex.data?.id).toBeTruthy();
  exerciseId = ex.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/skills/${publishedSkillId}`);
  await expect(page.getByRole("heading", { name: SKILL_NAME })).toBeVisible({
    timeout: 15_000,
  });
  // Exercise card renders with title + "multiple choice · 100 pts" meta.
  await expect(page.getByText("Pick the best prompt")).toBeVisible();
  await expect(page.getByText(/multiple choice · 100 pts/)).toBeVisible();
  // Learning content markdown rendered.
  await expect(page.getByRole("heading", { name: "Intro" })).toBeVisible();
});

// ── 6. MCQ attempt: validation → incorrect → correct feedback ──

test("MCQ attempt: empty-answer validation, incorrect then correct feedback", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/skills/${publishedSkillId}/exercises/${exerciseId}`);
  await expect(page.getByRole("heading", { name: "Pick the best prompt" })).toBeVisible({
    timeout: 15_000,
  });

  // Unhappy: submitting without a selection shows the client validation error.
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page.getByText("Please select an answer.")).toBeVisible();

  // Unhappy: wrong option → auto-graded incorrect with 0 pts + feedback.
  await page.getByText("Tell me stuff").click();
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page.getByText("❌ Incorrect — 0/100 pts")).toBeVisible({ timeout: 10_000 });
  // Feedback appears in the result banner AND (after refetch) in the attempt
  // history list — assert at least one instance.
  await expect(
    page.getByText(/Incorrect\. Explicit structure instructions win\./).first(),
  ).toBeVisible();

  // Happy: correct option → full marks + explanation feedback.
  await page.getByText("Return the answer as JSON with keys name and age").click();
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page.getByText("✅ Correct! — 100/100 pts")).toBeVisible({ timeout: 10_000 });

  // Attempt history section lists both attempts.
  await expect(page.getByRole("heading", { name: "Previous Attempts" })).toBeVisible();
  await expect(page.getByText("100/100", { exact: true })).toBeVisible();
  await expect(page.getByText("0/100", { exact: true })).toBeVisible();
});

// ── 7. Progress page reflects the completion ──

// APP BUG (sweep-skills #1): the progress page renders "undefined%" and
// "undefined/undefined" for every stat. The API returns the standard envelope
// { data: { skills_total, ... } } (verified via curl: GET
// /api/v1/orgs/{orgId}/progress/me → {"data":{"skills_total":1,...}}), but
// apps/web/src/app/(dashboard)/dashboard/orgs/[orgId]/progress/page.tsx types
// the query as apiWithAuth<ProgressData> and reads fields directly off the
// envelope (data.completion_percentage) instead of unwrapping data.data.
// Every other page uses apiWithAuth<{ data: T }>. Fix: unwrap the envelope.
test("my-progress page shows the completed skill and exercise stats", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/progress`);
  await expect(page.getByRole("heading", { name: "My Progress" })).toBeVisible({
    timeout: 15_000,
  });

  // Org has 2 skills (1 completed) and 1 exercise (1 done) → 50%.
  await expect(page.getByText("Skills Completed")).toBeVisible();
  await expect(page.getByText("1/2", { exact: true })).toBeVisible();
  await expect(page.getByText("Exercises Done")).toBeVisible();
  await expect(page.getByText("1/1", { exact: true })).toBeVisible();
  await expect(page.getByText("50%").first()).toBeVisible();
  await expect(page.getByText("Overall Progress")).toBeVisible();
});

// Coverage stand-in for the fixme above: the page at least loads with the
// stat-card scaffolding (labels render; values are broken by the bug).
test("my-progress page renders heading and stat card labels", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/progress`);
  await expect(page.getByRole("heading", { name: "My Progress" })).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByText("Skills Completed")).toBeVisible();
  await expect(page.getByText("Exercises Done")).toBeVisible();
  await expect(page.getByText("Overall Progress")).toBeVisible();
});

// ── 8. Learning path: create via UI, add skill item, publish ──

test("learning path: create via form, add skill item, publish via UI", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/paths/new`);
  await expect(page.locator("#name")).toBeVisible({ timeout: 15_000 });
  await page.locator("#name").fill(PATH_NAME);
  await page.locator("#description").fill("A structured journey through prompting.");
  await page.locator("#estimated_minutes").fill("120");
  await page.getByRole("button", { name: "Create Learning Path" }).click();

  await page.waitForURL(/\/paths\/[0-9A-HJKMNP-TV-Z]{26}$/, { timeout: 15_000 });
  // Detail page: editable name input holds the value; empty items state shows.
  await expect(page.locator(`input[value="${PATH_NAME}"]`)).toBeVisible();
  await expect(
    page.getByText("No items yet. Add skills, projects, or sections below."),
  ).toBeVisible();
  await expect(page.getByText("draft", { exact: true })).toBeVisible();

  // Add the published skill as a path item via the UI form.
  await page.locator("#add-item-type").selectOption("skill");
  await page.locator("#add-item-skill").selectOption(publishedSkillId);
  await page.getByRole("button", { name: "Add Item" }).click();

  // Item row renders: type chip "skill", the skill name, "required" chip.
  const itemRow = page
    .locator("div.rounded-lg.border")
    .filter({ hasText: SKILL_NAME })
    .filter({ has: page.getByRole("button", { name: "Remove" }) });
  await expect(itemRow).toBeVisible({ timeout: 10_000 });
  await expect(itemRow.getByText("skill", { exact: true })).toBeVisible();

  // Publish the path via the UI button; badge flips to "published".
  await page.getByRole("button", { name: "Publish", exact: true }).click();
  await expect(page.getByText("published", { exact: true })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByRole("button", { name: "Publish", exact: true })).not.toBeVisible();

  // The list page shows the published path card.
  await page.goto(`/dashboard/orgs/${orgId}/paths`);
  await expect(page.getByText(PATH_NAME)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("120 min")).toBeVisible();
});

// ── 9. Permission denied: student cannot create a skill (unhappy path) ──

test("student: create-skill form submission is rejected with a visible error", async () => {
  await loginInBrowser(page, student.email, "TestPass123!");

  await page.goto(`/dashboard/orgs/${orgId}/skills/new`);
  await expect(page.locator("#category")).toBeVisible({ timeout: 15_000 });
  await page.locator("#name").fill("Student Rogue Skill");
  await page.locator("#description").fill("Students must not be able to create skills.");
  await page.locator("#category").selectOption(categoryId);
  await page.getByRole("button", { name: "Create Skill" }).click();

  // 403 from the API surfaces in the red error banner; no navigation happens.
  await expect(page.getByText("Insufficient org permissions")).toBeVisible({
    timeout: 10_000,
  });
  await expect(page).toHaveURL(new RegExp(`/orgs/${orgId}/skills/new$`));
});

// ── 10. Draft visibility: student sees only published skills ──

test("student: skill list hides drafts and draft detail direct-nav fails", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/skills`);
  await expect(page.getByText(SKILL_NAME)).toBeVisible({ timeout: 15_000 });
  // The draft advanced skill must NOT appear for a student.
  await expect(page.getByText(DRAFT_SKILL_NAME)).not.toBeVisible();

  // Direct navigation to the draft skill's detail page → visible error state.
  await page.goto(`/dashboard/orgs/${orgId}/skills/${draftSkillId}`);
  await expect(page.getByText("Failed to load skill.")).toBeVisible({ timeout: 15_000 });
});
