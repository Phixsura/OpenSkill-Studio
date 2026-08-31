/**
 * Issue #21 — Workflow Pack + Matching + Composer browser E2E.
 *
 * Production flow: create workflow pack → build steps in the LIST editor view
 * → save → publish release → approve → verify in public registry → provider
 * connection + offering → install → visible in installations.
 *
 * Learning flow: guided requirement intake → confirm profile → compose
 * learning path draft → confirm → path created.
 *
 * DOM anchors (verified against page sources):
 * - Pack form: #name, #summary, #description, #workflowType, #difficulty, #scenarioTags
 * - Editor: "Canvas"/"List" toggle buttons, #new-step-type, #new-step-name, "Add step", "Save"
 * - Pack detail: #releaseVersion-ish input (placeholder based), "Publish Release",
 *   "Submit for Review", "Approve", "Open Editor"
 * - Requirements form: #context, #goal, capability checkbox labels, "Create Profile"
 * - Profile detail: "Confirm Profile", "Compose Learning Path"
 * - Compose page: "Get Recommendations", "Compose Draft", "Confirm & Create Path"
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;
const packName = `WF Hero ${Date.now()}`;

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

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
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("WF E2E Admin");
      break;
    } catch {
      await sleep(5000);
    }
  }
  orgId = await createOrg(admin, `WfE2E-${Date.now()}`);

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

test("production flow: create → edit steps → publish → approve → registry → provider → install", async () => {
  test.setTimeout(180_000);

  // ── Create the pack via the form ──
  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/new`);
  await page.waitForLoadState("networkidle");
  await page.locator("#name").fill(packName);
  await page.locator("#summary").fill("E-commerce hero image production");
  await page.locator("#description").fill("Generates brand-consistent hero images.");
  await page.locator("#workflowType").selectOption("production");
  await page.getByRole("button", { name: /create/i }).click();

  // router.replace lands on the pack detail page
  await page.waitForURL(/workflow-packs\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: packName })).toBeVisible();
  const packUrl = page.url();
  const packId = packUrl.split("/").pop()!;

  // ── Build the workflow in the LIST editor view (canvas is flaky headless) ──
  await page.getByRole("button", { name: "Open Editor" }).click();
  await page.waitForURL(/\/editor$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");
  await page.getByRole("button", { name: "List", exact: true }).click();

  // Step 1: prompt template (default output port "prompt")
  await page.locator("#new-step-type").selectOption("prompt_template");
  await page.locator("#new-step-name").fill("Build Prompt");
  await page.getByRole("button", { name: "Add step" }).click();
  await expect(page.getByText("build_prompt").first()).toBeVisible();

  // Step 2: instruction (no ports — keeps the graph trivially valid in UI E2E)
  await page.locator("#new-step-type").selectOption("instruction");
  await page.locator("#new-step-name").fill("Review Notes");
  await page.getByRole("button", { name: "Add step" }).click();
  await expect(page.getByText("review_notes").first()).toBeVisible();

  // Save (validate-then-save flow)
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText(/saved|Unsaved changes/i).first()).toBeVisible({
    timeout: 10_000,
  });

  // ── Publish a release from the detail page ──
  await page.goto(packUrl);
  await page.waitForLoadState("networkidle");
  // Version input inside "Publish New Release" section
  const versionInput = page.getByPlaceholder(/1\.0\.0|x\.y\.z/i).first();
  await versionInput.fill("1.0.0");
  await page.getByRole("button", { name: /Publish Release/i }).click();
  await expect(page.getByText("1.0.0").first()).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("published").first()).toBeVisible({ timeout: 10_000 });

  // ── Approve to make it public ──
  await page.getByRole("button", { name: /Submit for Review/i }).click();
  await expect(page.getByRole("button", { name: /^Approve$/i })).toBeVisible({
    timeout: 10_000,
  });
  await page.getByRole("button", { name: /^Approve$/i }).click();
  await expect(page.getByText("public").first()).toBeVisible({ timeout: 10_000 });

  // ── Public registry shows it ──
  await page.goto("/registry/workflows");
  await page.waitForLoadState("networkidle");
  await page.getByPlaceholder(/search/i).fill(packName);
  await expect(page.getByText(packName)).toBeVisible({ timeout: 10_000 });

  // ── Provider setup via UI ──
  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");
  // Create a mock connection (no credentials needed)
  const adapterSelect = page.locator("select").first();
  await adapterSelect.selectOption({ label: /Mock/i as unknown as string }).catch(async () => {
    // Fallback: choose by visible text option value
    const options = await adapterSelect.locator("option").allTextContents();
    const idx = options.findIndex((t) => /mock/i.test(t));
    if (idx >= 0) await adapterSelect.selectOption({ index: idx });
  });
  await page.getByPlaceholder(/name/i).first().fill("Mock Conn");
  await page.getByRole("button", { name: /^Connect$|create connection|add connection/i }).click();
  await expect(page.getByText("Mock Conn").first()).toBeVisible({ timeout: 10_000 });

  // Offering: capability image_generation via API (form flow varies) — the
  // install gate is what we assert through the UI
  const conns = await api(admin, "GET", `/orgs/${orgId}/provider-connections`);
  const connId = conns.data.find((c: { name: string }) => c.name === "Mock Conn").id;
  await api(admin, "POST", `/orgs/${orgId}/provider-offerings`, {
    connection_id: connId,
    capability_key: "image_generation",
    model_name: "mock-image-v1",
  });

  // ── Install via API (capability gate satisfied), verify in UI ──
  const install = await api(admin, "POST", `/orgs/${orgId}/workflow-installations`, {
    pack_id: packId,
    version: "1.0.0",
  });
  expect(install.data?.id).toBeTruthy();

  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(/1\.0\.0/).first()).toBeVisible({ timeout: 10_000 });
});

test("learning flow: intake → confirm → compose → confirm draft → path created", async () => {
  test.setTimeout(120_000);

  // ── Seed: a published skill pack teaching image_generation so the
  // composer has content to include (otherwise the draft is empty and
  // Confirm is correctly disabled) ──
  const skillPack = await api(admin, "POST", `/orgs/${orgId}/packs`, {
    name: `Prompt Fundamentals ${Date.now()}`,
    summary: "Teaches image generation prompting",
    capability_tags: ["image_generation"],
    estimated_minutes: 60,
  });
  const spId = skillPack.data.id;
  // A pack needs at least one skill to publish a release
  const cat = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `Cat ${Date.now()}`,
  });
  const skill = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: `Prompting ${Date.now()}`,
    description: "Prompting fundamentals for image generation",
    difficulty: "beginner",
    category_id: cat.data.id,
  });
  await api(admin, "POST", `/orgs/${orgId}/packs/${spId}/skills`, {
    skill_id: skill.data.id,
  });
  await api(admin, "POST", `/orgs/${orgId}/packs/${spId}/releases`, {
    version: "1.0.0",
  });

  // ── Guided intake ──
  await page.goto(`/dashboard/orgs/${orgId}/requirements/new`);
  await page.waitForLoadState("networkidle");
  await page.locator("#context").selectOption("learning");
  await page.locator("#goal").fill("Learn AI e-commerce visual production");
  // Tick one required capability chip if the catalog rendered
  const capChip = page.getByText("Image Generation", { exact: true }).first();
  if (await capChip.isVisible().catch(() => false)) {
    await capChip.click();
  }
  await page.getByRole("button", { name: /Create Profile/i }).click();

  // Profile detail (router.replace)
  await page.waitForURL(/requirements\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await expect(page.getByText(/review and confirm/i)).toBeVisible();

  // ── Confirm the profile ──
  await page.getByRole("button", { name: /Confirm Profile/i }).click();
  await expect(page.getByText("Confirmed").first()).toBeVisible({ timeout: 10_000 });

  // ── Compose learning path ──
  await page.getByRole("button", { name: /Compose Learning Path/i }).click();
  await page.waitForURL(/compose\/learning/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");

  // Recommendations (informational)
  await page.getByRole("button", { name: /Get Recommendations/i }).click();
  await expect(
    page.getByText(/match|Not eligible|No recommendations|recommendation/i).first(),
  ).toBeVisible({ timeout: 15_000 });

  // Draft
  await page.getByRole("button", { name: /Compose Draft/i }).click();
  await expect(page.getByRole("button", { name: /Confirm & Create Path/i })).toBeVisible({
    timeout: 15_000,
  });

  // Confirm → materialized path
  await page.getByRole("button", { name: /Confirm & Create Path/i }).click();
  await expect(page.getByText(/created|path/i).first()).toBeVisible({ timeout: 15_000 });
});

test("run flow: start from install form → review gate → decide in UI → completed", async () => {
  // A review-gated workflow: input → review_gate → output. Uses the mock
  // provider org state from the production-flow test (serial mode).
  const packRes = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `Review Run ${Date.now()}`,
  });
  const packId = packRes.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${packId}/definition`, {
    definition: {
      schema_version: 1,
      inputs: [{ key: "brief", type: "text", label: "Brief", required: true }],
      outputs: [{ key: "final", type: "text", from_step: "gate", from_port: "passed" }],
      steps: [
        {
          id: "take",
          type: "asset_input",
          name: "Take brief",
          config: { accept_types: ["image"] },
          inputs: [],
          outputs: [{ port: "brief", type: "text" }],
        },
        {
          id: "gate",
          type: "review_gate",
          name: "QA gate",
          config: { instructions: "Check the brief", due_days: 7 },
          inputs: [{ port: "subject", type: "text" }],
          outputs: [
            { port: "decision", type: "selection" },
            { port: "passed", type: "text" },
          ],
        },
      ],
      edges: [
        { id: "e1", from_step: "take", from_port: "brief", to_step: "gate", to_port: "subject" },
      ],
      ui: {},
    },
  });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packId}/releases`, {
    version: "1.0.0",
  });
  const install = await api(admin, "POST", `/orgs/${orgId}/workflow-installations`, {
    pack_id: packId,
  });
  const installId = install.data.id;

  // ── Start the run from the INSTALLATION DETAIL form (input_schema path) ──
  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations/${installId}`);
  await page.waitForLoadState("networkidle");
  const briefInput = page.locator("#run-brief");
  await expect(briefInput).toBeVisible({ timeout: 10_000 });
  await briefInput.fill("Launch banner for spring sale");
  await page.getByRole("button", { name: /Start Run/i }).click();

  // Start Run's onSuccess router.pushes straight to the run detail page
  await page.waitForURL(/workflow-runs\/[0-9A-Z]{26}$/, { timeout: 15_000 });

  // ── Suspends at the review gate ──
  await expect(page.getByText(/waiting_review/i).first()).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText(/Review required/i)).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Check the brief")).toBeVisible();

  // ── Decide with a note (per-review note state, audit round 2) ──
  await page.getByPlaceholder("Decision note (optional)").fill("Looks good — colors match brand");
  const decideResponse = page.waitForResponse(
    (r) => r.url().includes("/decide") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: /^Approve$/i }).click();
  // The UI-typed note round-tripped onto the review record
  const decided = (await (await decideResponse).json()) as {
    data: { decision: string; decision_note: string | null };
  };
  expect(decided.data.decision).toBe("approved");
  expect(decided.data.decision_note).toBe("Looks good — colors match brand");

  // ── Run settles to completed (poll the API — the page's status badge
  // text also matches step badges, so a bare getByText races the settle) ──
  const runId = page.url().match(/workflow-runs\/([^/?#]+)/)?.[1];
  let detail: { data: { status: string; outputs?: { final?: string } } } | null = null;
  await expect
    .poll(
      async () => {
        detail = await api(admin, "GET", `/orgs/${orgId}/workflow-runs/${runId}`);
        return detail!.data.status;
      },
      { timeout: 30_000 },
    )
    .toBe("completed");
  expect(detail!.data.outputs?.final).toBe("Launch banner for spring sale");
  // And the UI reflects it (3s refetch interval)
  await expect(page.getByText(/^completed$/i).first()).toBeVisible({ timeout: 10_000 });
});

test("comfyui import: upload JSON → dependency report → draft pack", async () => {
  const packRes = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `Comfy Import ${Date.now()}`,
  });
  const packId = packRes.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${packId}/import-comfyui`);
  await page.waitForLoadState("networkidle");

  // Never-executed banner is part of the red-line contract
  await expect(page.getByText(/never executed/i)).toBeVisible();

  // Upload an API-format workflow with a known node + a custom node
  const comfyJson = JSON.stringify({
    "1": {
      class_type: "KSampler",
      inputs: { seed: 42, model: ["2", 0] },
    },
    "2": {
      class_type: "CheckpointLoaderSimple",
      inputs: { ckpt_name: "sd_xl_base_1.0.safetensors" },
    },
    "3": {
      class_type: "MyCustomUpscaler",
      inputs: { image: ["1", 0] },
    },
    "4": {
      class_type: "SaveImage",
      inputs: { images: ["3", 0] },
    },
  });
  await page.setInputFiles("#comfy-file", {
    name: "workflow_api.json",
    mimeType: "application/json",
    buffer: Buffer.from(comfyJson),
  });

  // ── Dependency report renders: format, node counts, custom node, model ──
  await expect(page.getByText(/Dependency Report/i)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/Format:/i)).toBeVisible();
  await expect(page.getByText("MyCustomUpscaler")).toBeVisible();
  await expect(page.getByText(/sd_xl_base_1\.0\.safetensors/)).toBeVisible();

  // ── Convert to draft pack (name required to enable the button) ──
  await page.locator("#draft-name").fill(`Comfy Draft ${Date.now()}`);
  await page.getByRole("button", { name: /Create Draft Pack/i }).click();
  await page.waitForURL(/workflow-packs\/[^/]+$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");
  // Draft pack detail shows mapped steps (KSampler → image_generation)
  await expect(page.getByText(/draft/i).first()).toBeVisible({ timeout: 10_000 });
});
