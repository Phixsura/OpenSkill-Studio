/**
 * Sweep: REQUIREMENTS + MATCHING + COMPOSERS + CREATOR SHORTLIST.
 *
 * Covers what workflow-pack-flow.spec.ts skips:
 * - requirements LIST page (empty state → seeded profiles with status badges)
 * - profile detail EDIT (PATCH) via UI with provenance + typed persistence
 * - confirmed profile read-only UI
 * - production composer full flow (chain/template/placeholders/capability
 *   chips → confirm → Project created, visible under projects)
 * - production composer NO_WORKFLOWS_AVAILABLE gap
 * - learning composer NO_CONTENT_AVAILABLE gap (confirm disabled)
 * - compose from unconfirmed profile blocked (422 toast)
 * - creator shortlist: verified evidence, excluded list, two-click assign,
 *   creator responds (API — no respond UI page exists), status in UI
 * - shortlist on foreign-org project → 404 toast
 *
 * DOM anchors (verified against page sources):
 * - requirements list: "No requirement profiles yet.", status/context badges
 * - requirements/new: #goal, #time-budget, "Create Profile"
 * - profile detail: #field-<key> inputs, "Save Edits", "Confirm Profile",
 *   "You entered" provenance badges, "Compose Production Solution"
 * - compose/production: aria-label "Select confirmed profile",
 *   "Compose Solution", "Confirm & Create Project", gap alerts
 * - compose/learning: "Compose Draft", "Confirm & Create Path"
 * - shortlist: #profile, "Build Shortlist", "Assign", "Confirm offer?",
 *   "Verified evidence" details, "Not eligible (N)" details, status badges
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, addOrgMember, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
const ts = Date.now();

let admin: AuthContext;
let creator: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

// Cross-test state (serial mode)
let draftLearnProfileId: string; // draft learning profile (list test)
let prodProfileId: string; // confirmed production profile (composer + shortlist)
let uiProfileId: string; // profile created through the UI (edit + confirm tests)
let projectId: string; // project materialized by the production composer
const templateName = `Sweep Hero Template ${ts}`;
const packName = `Sweep Hero Pipeline ${ts}`;

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function api(auth: AuthContext, method: string, path: string, body?: object) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: auth.headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(`${method} ${path} -> ${res.status}: ${JSON.stringify(json)}`);
  }
  return json;
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  for (let i = 0; i < 3; i++) {
    try {
      admin = await registerUser("Sweep Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  creator = await registerUser("Sweep Creator");
  orgId = await createOrg(admin, `SweepMatch-${ts}`);
  await addOrgMember(admin, orgId, creator.userId, "student");

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

test("requirements list: empty state, then seeded profiles render with status badges", async () => {
  // Empty state first — brand-new org
  await page.goto(`/dashboard/orgs/${orgId}/requirements`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("No requirement profiles yet.")).toBeVisible({ timeout: 15_000 });

  // Seed: a draft learning profile + a confirmed production profile (API)
  const draftRes = await api(admin, "POST", `/orgs/${orgId}/requirement-profiles`, {
    context_type: "learning",
    structured_requirements: { goal: "Master motion design basics" },
  });
  draftLearnProfileId = draftRes.data.id;

  const prodRes = await api(admin, "POST", `/orgs/${orgId}/requirement-profiles`, {
    context_type: "production",
    structured_requirements: {
      goal: "Produce hero imagery at scale",
      output_type: "image",
      required_capabilities: ["image_generation", "background_removal"],
    },
  });
  prodProfileId = prodRes.data.id;
  await api(admin, "POST", `/orgs/${orgId}/requirement-profiles/${prodProfileId}/confirm`);

  // List renders both with correct status + context badges
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Master motion design basics")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Produce hero imagery at scale")).toBeVisible();
  await expect(page.getByText("draft", { exact: true })).toBeVisible();
  await expect(page.getByText("confirmed", { exact: true })).toBeVisible();
  await expect(page.getByText("learning", { exact: true })).toBeVisible();
  await expect(page.getByText("production", { exact: true })).toBeVisible();

  // Card click-through navigates to the profile detail
  await page.getByText("Master motion design basics").click();
  await page.waitForURL(new RegExp(`requirements/${draftLearnProfileId}$`), { timeout: 15_000 });
  await expect(page.getByText(/review and confirm/i)).toBeVisible();
});

test("new requirement: UI validation error, then create + edit — provenance & typed values persist after reload", async () => {
  test.setTimeout(90_000);

  await page.goto(`/dashboard/orgs/${orgId}/requirements/new`);
  await page.waitForLoadState("networkidle");

  // ── Unhappy: out-of-range time budget surfaces the API validation error ──
  await page.locator("#goal").fill("Learn AI e-commerce visual production");
  await page.locator("#time-budget").fill("999999");
  await page.getByRole("button", { name: /Create Profile/i }).click();
  await expect(page.getByText(/must be minutes/i)).toBeVisible({ timeout: 10_000 });

  // ── Happy: fix the budget, create, land on the review screen ──
  await page.locator("#time-budget").fill("300");
  await page.getByRole("button", { name: /Create Profile/i }).click();
  await page.waitForURL(/requirements\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  uiProfileId = page.url().split("/").pop()!;
  await expect(page.getByText(/review and confirm/i)).toBeVisible();

  // Form-entered fields carry "You entered" provenance (goal + time_budget)
  await expect(page.getByText("You entered")).toHaveCount(2);

  // ── Edit via UI: change goal, budget; add required capabilities (list) ──
  await page.locator("#field-goal").fill("Master AI e-commerce hero production");
  await page.locator("#field-time_budget").fill("240");
  await page.locator("#field-required_capabilities").fill("image_generation");
  await page.getByRole("button", { name: /Save Edits/i }).click();
  await expect(page.getByText("Profile updated")).toBeVisible({ timeout: 10_000 });

  // ── Reload: edits + provenance persisted ──
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.locator("#field-goal")).toHaveValue("Master AI e-commerce hero production");
  await expect(page.locator("#field-time_budget")).toHaveValue("240");
  await expect(page.locator("#field-required_capabilities")).toHaveValue("image_generation");
  // required_capabilities edit promoted its provenance → 3 badges now
  await expect(page.getByText("You entered")).toHaveCount(3);

  // Typed persistence: number stayed a number, list stayed a list (API check)
  const detail = await api(admin, "GET", `/orgs/${orgId}/requirement-profiles/${uiProfileId}`);
  expect(detail.data.structured_requirements.time_budget).toBe(240);
  expect(detail.data.structured_requirements.required_capabilities).toEqual(["image_generation"]);
  expect(detail.data.extraction_meta.provenance.required_capabilities).toBe("user_entered");
});

test("confirmed profile is read-only in the UI", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/requirements/${uiProfileId}`);
  await page.waitForLoadState("networkidle");

  await page.getByRole("button", { name: /Confirm Profile/i }).click();
  await expect(page.getByText("Confirmed").first()).toBeVisible({ timeout: 10_000 });

  // Inputs disabled, edit controls gone, compose actions appear
  await expect(page.locator("#field-goal")).toBeDisabled();
  await expect(page.locator("#field-time_budget")).toBeDisabled();
  await expect(page.getByRole("button", { name: /Save Edits/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Confirm Profile/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Compose Learning Path/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Compose Production Solution/i })).toBeVisible();
});

test("unhappy: composing a production solution from an UNCONFIRMED profile is blocked", async () => {
  // draftLearnProfileId is still draft — deep-link it into the composer
  await page.goto(`/dashboard/orgs/${orgId}/compose/production?profile=${draftLearnProfileId}`);
  await page.waitForLoadState("networkidle");

  // It is not in the confirmed-profiles dropdown, but the URL param arms the
  // button — the API rejects with PROFILE_NOT_CONFIRMED, surfaced as a toast.
  await page.getByRole("button", { name: /Compose Solution/i }).click();
  await expect(page.getByText(/must be confirmed before composing/i)).toBeVisible({
    timeout: 10_000,
  });
});

test("learning composer: no teaching content → NO_CONTENT_AVAILABLE gap, confirm disabled", async () => {
  // Confirmed learning profile requiring a capability nothing teaches
  const res = await api(admin, "POST", `/orgs/${orgId}/requirement-profiles`, {
    context_type: "learning",
    structured_requirements: {
      goal: "Learn voice cloning production",
      required_capabilities: ["voice_generation"],
    },
  });
  const pid = res.data.id;
  await api(admin, "POST", `/orgs/${orgId}/requirement-profiles/${pid}/confirm`);

  await page.goto(`/dashboard/orgs/${orgId}/compose/learning?profile=${pid}`);
  await page.waitForLoadState("networkidle");
  await page.getByRole("button", { name: /Compose Draft/i }).click();

  await expect(page.getByText(/No content available for "voice_generation"/)).toBeVisible({
    timeout: 15_000,
  });
  // Empty draft — the confirm gate stays closed
  await expect(page.getByRole("button", { name: /Confirm & Create Path/i })).toBeDisabled();
});

test("production composer: no eligible workflows → NO_WORKFLOWS_AVAILABLE + template gap, confirm disabled", async () => {
  // Confirmed production profile whose hard constraints no pack satisfies
  const res = await api(admin, "POST", `/orgs/${orgId}/requirement-profiles`, {
    context_type: "production",
    structured_requirements: {
      goal: "Generate audiobook narration",
      output_type: "audio",
      required_capabilities: ["voice_generation"],
    },
  });
  const pid = res.data.id;
  await api(admin, "POST", `/orgs/${orgId}/requirement-profiles/${pid}/confirm`);

  await page.goto(`/dashboard/orgs/${orgId}/compose/production?profile=${pid}`);
  await page.waitForLoadState("networkidle");
  await page.getByRole("button", { name: /Compose Solution/i }).click();

  // Shared-DB-robust: the dev DB may already hold public voice_generation
  // packs (S2 survivors), none of which produce `audio`. So the composer
  // correctly reports "no usable workflow" via EITHER gap family —
  // NO_WORKFLOWS_AVAILABLE (zero survivors) or NO_WORKFLOW_FOR_OUTPUT
  // (survivors can't produce the requested output). Assert on the gap, not
  // on the empty-chain branch which only shows when survivors are literally 0.
  await expect(
    page.getByText(/NO_WORKFLOWS_AVAILABLE|NO_WORKFLOW_FOR_OUTPUT/),
  ).toBeVisible({ timeout: 15_000 });
  // No org template exists in this fresh org — the inline note + the gate both hold
  await expect(page.getByText(/No project template matched/)).toBeVisible();
  await expect(page.getByRole("button", { name: /Confirm & Create Project/i })).toBeDisabled();
});

test("production composer full flow: chain + template + placeholders + ready capabilities → project created", async () => {
  test.setTimeout(90_000);

  // ── Seed (API): published+approved workflow pack with image output ──
  const packRes = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: packName,
    summary: "Hero image generation + background removal",
    workflow_type: "production",
  });
  const packId = packRes.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${packId}/definition`, {
    definition: {
      schema_version: 1,
      inputs: [{ key: "brief", type: "prompt", label: "Brief", required: true }],
      outputs: [{ key: "hero", type: "image", from_step: "cleanup", from_port: "clean" }],
      steps: [
        {
          id: "take",
          type: "asset_input",
          name: "Take brief",
          config: { accept_types: ["image"] },
          inputs: [],
          outputs: [{ port: "brief", type: "prompt" }],
        },
        {
          id: "gen",
          type: "provider_action",
          name: "Generate hero",
          config: { capability: "image_generation" },
          inputs: [{ port: "prompt", type: "prompt" }],
          outputs: [{ port: "image", type: "image" }],
        },
        {
          id: "cleanup",
          type: "provider_action",
          name: "Remove background",
          config: { capability: "background_removal" },
          inputs: [{ port: "image", type: "image" }],
          outputs: [{ port: "clean", type: "image" }],
        },
      ],
      edges: [
        { id: "e1", from_step: "take", from_port: "brief", to_step: "gen", to_port: "prompt" },
        { id: "e2", from_step: "gen", from_port: "image", to_step: "cleanup", to_port: "image" },
      ],
      ui: {},
    },
  });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packId}/releases`, {
    version: "1.0.0",
    dependencies: {
      requires_capabilities: [
        { capability: "image_generation" },
        { capability: "background_removal" },
      ],
    },
  });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packId}/submit-review`);
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packId}/approve`);

  // ── Seed: project template (org-scoped, matched by the composer) ──
  await api(admin, "POST", `/orgs/${orgId}/project-templates`, {
    name: templateName,
    description: "Hero production project",
    instructions: "Produce brand-consistent hero images.",
    project_type: "general",
    difficulty: "intermediate",
    rubric: [{ criterion: "Visual quality", max_score: 100 }],
  });

  // ── Seed: mock provider offerings so capabilities read "ready" ──
  const adapters = await api(admin, "GET", `/providers/adapters`);
  const mock = adapters.data.find((a: { key: string }) => a.key === "mock");
  const conn = await api(admin, "POST", `/orgs/${orgId}/provider-connections`, {
    adapter_id: mock.id,
    name: "Sweep Mock",
  });
  for (const cap of ["image_generation", "background_removal"]) {
    await api(admin, "POST", `/orgs/${orgId}/provider-offerings`, {
      connection_id: conn.data.id,
      capability_key: cap,
      model_name: `mock-${cap}`,
    });
  }

  // ── Compose in the UI ──
  await page.goto(`/dashboard/orgs/${orgId}/compose/production?profile=${prodProfileId}`);
  await page.waitForLoadState("networkidle");
  await page.getByRole("button", { name: /Compose Solution/i }).click();

  // Draft renders: the chain picked a Sweep Hero pipeline pack. (Public
  // approved packs from previous test runs stay eligible — rank order among
  // them is not deterministic, so match the family, not this run's exact ts.)
  await expect(page.getByText(/Sweep Hero Pipeline/).first()).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(`Project template:`)).toBeVisible();
  await expect(page.getByText(templateName).first()).toBeVisible();
  // Unresolved prompt input is a first-class placeholder, never silently filled
  await expect(page.getByText(/provided by you at run time/)).toBeVisible();
  // Capability roll-up chips show provider readiness
  await expect(page.getByText("image_generation · ready")).toBeVisible();
  await expect(page.getByText("background_removal · ready")).toBeVisible();

  // ── Human confirm → Project materialized ──
  await page.getByRole("button", { name: /Confirm & Create Project/i }).click();
  await expect(page.getByText("Project created.").first()).toBeVisible({ timeout: 15_000 });

  // Open the project — title comes from the template
  await page.getByRole("link", { name: /Open the project/i }).click();
  await page.waitForURL(/projects\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  projectId = page.url().match(/projects\/([0-9A-Z]{26})/)![1]!;
  await expect(page.getByRole("heading", { name: templateName })).toBeVisible({
    timeout: 15_000,
  });

  // And it is listed under the org's projects
  await page.goto(`/dashboard/orgs/${orgId}/projects`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(templateName).first()).toBeVisible({ timeout: 10_000 });
});

test("creator shortlist: evidence renders, excluded is transparent, assign → offer → creator accepts", async () => {
  test.setTimeout(90_000);

  // ── Seed evidence: creator completes a skill tagged with both capabilities ──
  const cat = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `Sweep Cat ${ts}`,
  });
  const skill = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: `Sweep Hero Skill ${ts}`,
    description: "Hero image production skills",
    difficulty: "beginner",
    category_id: cat.data.id,
    tags: ["image_generation", "background_removal"],
  });
  const skillId = skill.data.id;
  await api(admin, "POST", `/orgs/${orgId}/skills/${skillId}/publish`);
  const exercise = await api(admin, "POST", `/orgs/${orgId}/skills/${skillId}/exercises`, {
    title: "Pick the right answer",
    description: "MCQ",
    type: "multiple_choice",
    config: { question: "Best practice?", options: ["a", "b"], correct: ["a"] },
    max_score: 100,
  });
  // Creator passes the exercise → skill COMPLETED → verified evidence
  await api(creator, "POST", `/orgs/${orgId}/exercises/${exercise.data.id}/attempts`, {
    answer: { selected: ["a"] },
  });

  // ── Build the shortlist in the UI ──
  await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}/shortlist`);
  await page.waitForLoadState("networkidle");
  await page.locator(`option[value="${prodProfileId}"]`).waitFor({ state: "attached" });
  await page.locator("#profile").selectOption(prodProfileId);
  await page.getByRole("button", { name: /Build Shortlist/i }).click();

  // Ranked creator card with evidence detail
  await expect(page.getByText("Sweep Creator")).toBeVisible({ timeout: 20_000 });
  await page.getByText("Verified evidence", { exact: true }).click();
  await expect(page.getByText("image_generation").first()).toBeVisible();
  await expect(page.getByText(/skill completed/).first()).toBeVisible();

  // Excluded list is transparent: admin has no verified evidence
  await page.getByText(/Not eligible \(\d+\)/).click();
  await expect(page.getByText(admin.userId)).toBeVisible();
  await expect(page.getByText(/No verified evidence/).first()).toBeVisible();

  // ── Two-click assign → offer created ──
  await page.getByRole("button", { name: "Assign", exact: true }).click();
  await page.getByRole("button", { name: /Confirm offer\?/i }).click();
  await expect(page.getByText(/Assignment offered/i).first()).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Assignments")).toBeVisible();
  await expect(page.getByText(creator.userId)).toBeVisible();
  await expect(page.getByText("offered", { exact: true })).toBeVisible();
  // Ranked card flips to "Already offered"
  await expect(page.getByText("Already offered")).toBeVisible();

  // ── Creator accepts. There is NO respond UI page (opportunities page only
  // lists client briefs; no assignments page exists) — respond via API as the
  // creator, then verify the status change lands in the shortlist UI. ──
  const assignments = await api(
    admin,
    "GET",
    `/orgs/${orgId}/creator-assignments?project_id=${projectId}`,
  );
  const assignmentId = assignments.data[0].id;
  await api(creator, "POST", `/orgs/${orgId}/creator-assignments/${assignmentId}/respond`, {
    accept: true,
  });

  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("accepted", { exact: true })).toBeVisible({ timeout: 10_000 });
});

test("unhappy: shortlist on a foreign org's project → Project not found", async () => {
  // Creator owns a second org with its own project
  const org2 = await createOrg(creator, `SweepForeign-${ts}`);
  const foreign = await api(creator, "POST", `/orgs/${org2}/projects`, {
    title: "Foreign Project",
    description: "Belongs to another org",
    instructions: "n/a",
    rubric: [{ criterion: "Quality", max_score: 10 }],
  });

  await page.goto(`/dashboard/orgs/${orgId}/projects/${foreign.data.id}/shortlist`);
  await page.waitForLoadState("networkidle");
  await page.locator(`option[value="${prodProfileId}"]`).waitFor({ state: "attached" });
  await page.locator("#profile").selectOption(prodProfileId);
  await page.getByRole("button", { name: /Build Shortlist/i }).click();

  await expect(page.getByText(/Project not found/i)).toBeVisible({ timeout: 10_000 });
});
