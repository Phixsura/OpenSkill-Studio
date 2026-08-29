/**
 * Sweep: WORKFLOW PACKS DEEP — editor edge interactions.
 *
 * Complements workflow-pack-flow.spec.ts (which covers the production
 * publish→approve→registry→install flow). This spec drills into the editor
 * itself: canvas node rendering, list-view port wiring, type-mismatch
 * blocking, the validation error panel (pointer navigation), the port-rename
 * edge cascade, step deletion edge cleanup, save/reload round-trip with
 * position persistence, plus unhappy paths (empty list state, publish with
 * empty definition, duplicate release version) and archive via UI.
 *
 * DOM anchors (verified against page sources):
 * - list page: "New Workflow Pack" button, "No workflow packs found." empty state
 * - new form: #name #summary #description #workflowType #difficulty #scenarioTags
 * - editor: "Canvas"/"List" toggle, #new-step-type, #new-step-name, "Add step",
 *   "Auto-layout", "Save", "Unsaved changes" badge, role=alert error panel
 * - list view <ol><li> per step, AddConnectionRow selects with aria-labels
 *   "Target input port" / "Source step" / "Source output port", "Connect"
 * - config panel: "Input ports name 1", "Input ports type 1", "Delete step"
 * - IOSection: "Add output", "Output source step 1", "Output source port 1"
 * - detail page: aria-label "Release version", "Publish Release",
 *   "Archive Pack" (window.confirm)
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

const packName = `Sweep Deep Pack ${Date.now()}`;
const emptyPackName = `Sweep Empty Pack ${Date.now()}`;
let packUrl = "";
let packId = "";
let emptyPackId = "";

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

/** Editor list-view <li> for a step. Anchors on the step HEADER BUTTON —
 * plain hasText matches other lis too, because every AddConnectionRow's
 * "Source step" select embeds all other steps' names as option text. */
function stepLi(name: string) {
  return page
    .locator("ol > li")
    .filter({ has: page.getByRole("button", { name: new RegExp(`^${name}`) }) });
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("Sweep WFDeep Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  orgId = await createOrg(admin, `SweepWfDeep-${Date.now()}`);

  ctx = await browser.newContext();
  page = await ctx.newPage();
  // Accept window.confirm (archive) and any beforeunload prompts.
  page.on("dialog", (d) => d.accept().catch(() => {}));
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

test("empty list state → create pack via UI form", async () => {
  // Fresh org: the list shows the empty state (unhappy/empty path)
  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("No workflow packs found.")).toBeVisible();

  // Navigate to the form through the real button
  await page.getByRole("button", { name: "New Workflow Pack" }).click();
  await page.waitForURL(/workflow-packs\/new$/, { timeout: 15_000 });

  // Native required blocks an empty submit (stays on the form)
  await page.getByRole("button", { name: /Create Workflow Pack/i }).click();
  await expect(page).toHaveURL(/workflow-packs\/new$/);

  await page.locator("#name").fill(packName);
  await page.locator("#summary").fill("Deep editor interaction sweep");
  await page.locator("#description").fill("Exercises canvas, wiring, renames, deletes.");
  await page.locator("#workflowType").selectOption("production");
  await page.locator("#difficulty").selectOption("intermediate");
  await page.locator("#scenarioTags").fill("ecommerce, hero-images");
  await page.getByRole("button", { name: /Create Workflow Pack/i }).click();

  await page.waitForURL(/workflow-packs\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  packUrl = page.url();
  packId = packUrl.split("/").pop()!;
  await expect(page.getByRole("heading", { name: packName })).toBeVisible();
  await expect(page.getByText("draft").first()).toBeVisible();
  await expect(page.getByText("production").first()).toBeVisible();
  // No steps yet — detail page empty state for the definition
  await expect(page.getByText(/No steps yet/i)).toBeVisible();
});

test("editor: add two steps in list view → canvas renders both nodes", async () => {
  await page.getByRole("button", { name: "Open Editor" }).click();
  await page.waitForURL(/\/editor$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");

  await page.getByRole("button", { name: "List", exact: true }).click();

  // Add-step button is disabled until a name is typed (inline validation)
  await expect(page.getByRole("button", { name: "Add step" })).toBeDisabled();

  await page.locator("#new-step-type").selectOption("prompt_template");
  await page.locator("#new-step-name").fill("Build Prompt");
  await page.getByRole("button", { name: "Add step" }).click();
  await expect(page.getByText("build_prompt").first()).toBeVisible();

  await page.locator("#new-step-type").selectOption("provider_action");
  await page.locator("#new-step-name").fill("Generate Image");
  await page.getByRole("button", { name: "Add step" }).click();
  await expect(page.getByText("generate_image").first()).toBeVisible();

  // Dirty badge appears after edits
  await expect(page.getByText("Unsaved changes")).toBeVisible();

  // Switch to CANVAS — both React Flow nodes render with name + type label
  await page.getByRole("button", { name: "Canvas", exact: true }).click();
  await expect(page.locator(".react-flow__node")).toHaveCount(2);
  const buildNode = page.locator('.react-flow__node[data-id="build_prompt"]');
  const genNode = page.locator('.react-flow__node[data-id="generate_image"]');
  await expect(buildNode).toBeVisible();
  await expect(buildNode.getByText("Build Prompt")).toBeVisible();
  await expect(buildNode.getByText("Prompt Template")).toBeVisible();
  await expect(genNode).toBeVisible();
  await expect(genNode.getByText("Provider Action")).toBeVisible();
});

test("list view: wire an edge via the from/port selects", async () => {
  await page.getByRole("button", { name: "List", exact: true }).click();

  const li = stepLi("Generate Image");
  await expect(li.getByText("Connections in")).toBeVisible();
  await li.getByLabel("Target input port").selectOption("prompt");
  await li.getByLabel("Source step").selectOption("build_prompt");
  await li.getByLabel("Source output port").selectOption("prompt");
  await li.getByRole("button", { name: "Connect" }).click();

  // Edge row renders in the connections table
  await expect(page.getByText("build_prompt.prompt → prompt")).toBeVisible();
});

test("type mismatch: UI blocks incompatible port wiring; save maps WF_EDGE_TYPE_MISMATCH to the error panel", async () => {
  // Add a review_gate — its `subject` input is type image
  await page.locator("#new-step-type").selectOption("review_gate");
  await page.locator("#new-step-name").fill("QA Gate");
  await page.getByRole("button", { name: "Add step" }).click();
  await expect(page.getByText("qa_gate").first()).toBeVisible();

  // Attempt image-typed input fed from a prompt-typed output: the source
  // port select filters by the coercion matrix, leaving only the placeholder.
  const gateLi = stepLi("QA Gate");
  await gateLi.getByLabel("Target input port").selectOption("subject");
  await gateLi.getByLabel("Source step").selectOption("build_prompt");
  await expect(gateLi.getByLabel("Source output port").locator("option")).toHaveCount(1);
  await expect(gateLi.getByRole("button", { name: "Connect" })).toBeDisabled();

  // Force a mismatch through the config panel: retype generate_image's
  // input port from prompt → image while the prompt-typed edge exists.
  // (Port TYPE changes do not cascade edge removal — only renames do.)
  await stepLi("Generate Image")
    .getByRole("button", { name: /Generate Image/ })
    .click();
  await expect(page.getByRole("heading", { name: "Provider Action" })).toBeVisible();
  await page.getByLabel("Input ports type 1").selectOption("image");

  await page.getByRole("button", { name: "Save", exact: true }).click();

  // Error panel (role=alert) with machine codes + pointers
  const panel = page.getByRole("alert");
  await expect(panel).toBeVisible({ timeout: 10_000 });
  await expect(panel.getByText("WF_EDGE_TYPE_MISMATCH")).toBeVisible();
  await expect(panel.getByText(/Cannot connect prompt → image/)).toBeVisible();
  // qa_gate.subject has no incoming edge → also surfaced, with pointer
  await expect(panel.getByText("WF_INPUT_UNSATISFIED")).toBeVisible();
  await expect(panel.getByText(/\/steps\/2\/inputs\/subject/)).toBeVisible();

  // Clicking an error navigates to its step (pointer → step select)
  await panel.getByText("WF_INPUT_UNSATISFIED").click();
  await expect(page.getByRole("heading", { name: "Review Gate" })).toBeVisible();

  // Revert the type so later tests work with a coherent graph
  await stepLi("Generate Image")
    .getByRole("button", { name: /Generate Image/ })
    .click();
  await page.getByLabel("Input ports type 1").selectOption("prompt");
});

test("rename a port in the config panel: connected edge survives (rename cascade)", async () => {
  // generate_image is selected from the previous test; rename its input port
  await expect(page.getByRole("heading", { name: "Provider Action" })).toBeVisible();
  await page.getByLabel("Input ports name 1").fill("prompt_in");

  // The edge was REWRITTEN to the new port name — not dropped
  await expect(page.getByText("build_prompt.prompt → prompt_in")).toBeVisible();
  await expect(stepLi("Generate Image").getByText(/in: prompt_in:prompt/)).toBeVisible();
});

test("delete a step: its edges disappear from the list view", async () => {
  // Delete the edge's SOURCE step
  await stepLi("Build Prompt")
    .getByRole("button", { name: /Build Prompt/ })
    .click();
  await expect(page.getByRole("heading", { name: "Prompt Template" })).toBeVisible();
  await page.getByRole("button", { name: "Delete step" }).click();

  await expect(stepLi("Build Prompt")).toHaveCount(0);
  await expect(page.getByText("build_prompt.prompt → prompt_in")).toHaveCount(0);

  // Also remove the dangling QA Gate to restore a publishable graph
  await stepLi("QA Gate")
    .getByRole("button", { name: /QA Gate/ })
    .click();
  await page.getByRole("button", { name: "Delete step" }).click();
  await expect(stepLi("QA Gate")).toHaveCount(0);

  // Re-wire a fresh source so the graph validates again
  await page.locator("#new-step-type").selectOption("prompt_template");
  await page.locator("#new-step-name").fill("Fresh Prompt");
  await page.getByRole("button", { name: "Add step" }).click();
  const genLi = stepLi("Generate Image");
  await genLi.getByLabel("Target input port").selectOption("prompt_in");
  await genLi.getByLabel("Source step").selectOption("fresh_prompt");
  await genLi.getByLabel("Source output port").selectOption("prompt");
  await genLi.getByRole("button", { name: "Connect" }).click();
  await expect(page.getByText("fresh_prompt.prompt → prompt_in")).toBeVisible();
});

test("declare workflow output, save → reload: definition round-trips with positions", async () => {
  // Set generate_image's capability — a provider_action with an empty
  // capability now fails validation on save (R83 min_length=1), so the test
  // must pick one before it can save a valid definition.
  await stepLi("Generate Image")
    .getByRole("button", { name: /Generate Image/ })
    .click();
  await page.locator("#cfg-capability").selectOption("image_generation");

  // Declare a workflow output through the IOSection selects
  await page.getByRole("button", { name: "Add output" }).click();
  await page.getByLabel("Output source step 1").selectOption("generate_image");
  await page.getByLabel("Output source port 1").selectOption("result");
  await expect(page.getByLabel("Output key 1")).toHaveValue("output_1");

  // Auto-layout assigns dagre positions, then save
  await page.getByRole("button", { name: "Auto-layout" }).click();
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Workflow saved")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Unsaved changes")).toHaveCount(0);

  // Positions were persisted server-side
  const detail = await api(admin, "GET", `/orgs/${orgId}/workflow-packs/${packId}`);
  const positions = detail.data.definition.ui.positions as Record<string, [number, number]>;
  expect(positions.fresh_prompt).toBeDefined();
  expect(positions.generate_image).toBeDefined();

  // Reload the editor — steps, edge, output, and positions all round-trip
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("button", { name: "Canvas", exact: true })).toBeVisible({
    timeout: 15_000,
  });

  // Canvas is the default view: both nodes at their saved coordinates
  await expect(page.locator(".react-flow__node")).toHaveCount(2);
  const [gx, gy] = positions.generate_image!;
  await expect(page.locator('.react-flow__node[data-id="generate_image"]')).toHaveCSS(
    "transform",
    `matrix(1, 0, 0, 1, ${gx}, ${gy})`,
  );
  const [fx, fy] = positions.fresh_prompt!;
  await expect(page.locator('.react-flow__node[data-id="fresh_prompt"]')).toHaveCSS(
    "transform",
    `matrix(1, 0, 0, 1, ${fx}, ${fy})`,
  );

  // List view still shows both steps and the surviving edge
  await page.getByRole("button", { name: "List", exact: true }).click();
  await expect(stepLi("Fresh Prompt").first()).toBeVisible();
  await expect(stepLi("Generate Image").first()).toBeVisible();
  await expect(page.getByText("fresh_prompt.prompt → prompt_in")).toBeVisible();
  await expect(page.getByLabel("Output key 1")).toHaveValue("output_1");
});

test("unhappy: publishing a release with an empty definition shows a visible error", async () => {
  const res = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: emptyPackName,
  });
  emptyPackId = res.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${emptyPackId}`);
  await page.waitForLoadState("networkidle");
  await page.getByLabel("Release version").fill("1.0.0");
  await page.getByRole("button", { name: /Publish Release/i }).click();

  // EMPTY_DEFINITION error surfaces as a toast
  await expect(page.getByText("Workflow definition has no steps")).toBeVisible({
    timeout: 10_000,
  });
  // And no release was created
  await expect(page.getByText("No releases yet.")).toBeVisible();
});

test("unhappy: duplicate release version shows a visible error", async () => {
  await page.goto(packUrl);
  await page.waitForLoadState("networkidle");

  // First publish succeeds (definition saved in the round-trip test)
  await page.getByLabel("Release version").fill("1.0.0");
  await page.getByRole("button", { name: /Publish Release/i }).click();
  await expect(page.getByText("v1.0.0")).toBeVisible({ timeout: 10_000 });

  // Same version again → VERSION_EXISTS surfaces in the UI
  await page.getByLabel("Release version").fill("1.0.0");
  await page.getByRole("button", { name: /Publish Release/i }).click();
  await expect(page.getByText("Version 1.0.0 already released")).toBeVisible({
    timeout: 10_000,
  });
});

test("archive pack via UI: confirm dialog → removed from the list", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${emptyPackId}`);
  await page.waitForLoadState("networkidle");

  // window.confirm auto-accepted by the beforeAll dialog handler
  await page.getByRole("button", { name: "Archive Pack" }).click();
  await page.waitForURL(/workflow-packs$/, { timeout: 15_000 });
  await page.waitForLoadState("networkidle");

  // Archived pack is filtered out of the default list; the live one remains
  await expect(page.getByText(packName)).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(emptyPackName)).toHaveCount(0);
});
