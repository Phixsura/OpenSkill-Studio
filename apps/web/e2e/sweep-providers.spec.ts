/**
 * Sweep: PROVIDERS + CREDENTIALS + BINDINGS + INSTALLATIONS + RUNS-LIST.
 *
 * Pages exercised (DOM anchors read from page sources, never guessed):
 * - /dashboard/orgs/[orgId]/providers
 *     adapter select aria-label "Provider adapter", name placeholder
 *     "Connection name", cred input #cred-<field> (type=password),
 *     "Connect" button, per-card "Delete" → "Confirm delete?" armed flow,
 *     offering form: aria-labels "Connection", "Capability", "Quality tier",
 *     placeholder "Model name", "Add Offering" button.
 * - /dashboard/orgs/[orgId]/workflow-installations (list, empty state)
 * - /dashboard/orgs/[orgId]/workflow-installations/[installId]
 *     bindings: selects aria-label "Offering for <step>" / "Binding mode for
 *     <step>", "Confirm" button, badges "suggested"/"confirmed", red gap text;
 *     upgrade: #diff-version + "Show Diff", #upgrade-version + "Apply";
 *     manage: "Remove" (window.confirm).
 * - /dashboard/orgs/[orgId]/workflow-runs (list, empty state, status badges,
 *     pagination block only when total > 20)
 *
 * NOT covered because the UI does not expose them (verified in page source):
 * - health-check button (none exists on the providers page)
 * - DELETE offering via UI (offerings table has no delete/deactivate control;
 *   covered indirectly: deleting the connection cascades its offerings)
 * - negative-cost offering (the UI form has no cost field; server-side 422
 *   asserted via API inside the offering test)
 *
 * Does NOT duplicate the run→review flow in workflow-pack-flow.spec.ts —
 * runs here are API-seeded purely to exercise the runs LIST page.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, addOrgMember, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

let packAId: string; // image_generation provider_action — satisfiable
let packBId: string; // text_to_video provider_action — NO offering (gap)
let installAId = "";
let installBId = "";
let offeringId = "";
let runCompletedId = "";
let runFailedId = "";

const MOCK_CONN = "Mock Sweep Conn";
const ANTHROPIC_CONN = "Anthropic Sweep Conn";
const SECRET = "sk-ant-sweep-secret-XYZ-9f8e7d";
const MODEL = "mock-image-xl";

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

/** API helper returning status + parsed body (204-safe). */
async function api(
  auth: AuthContext,
  method: string,
  path: string,
  body?: object,
): Promise<{ status: number; body: any }> {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: auth.headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  let json: any = null;
  try {
    json = await res.json();
  } catch {
    /* 204 no content */
  }
  return { status: res.status, body: json };
}

// ── Workflow definitions (validated against schemas/workflow_definition.py) ──

const DEF_A_V1 = {
  schema_version: 1,
  inputs: [{ key: "prompt", type: "prompt", label: "Prompt", required: true }],
  outputs: [{ key: "final_image", type: "image", from_step: "gen", from_port: "image" }],
  steps: [
    {
      id: "take",
      type: "asset_input",
      name: "Take prompt",
      config: { accept_types: ["image"] },
      inputs: [],
      outputs: [{ port: "prompt", type: "prompt" }],
    },
    {
      id: "gen",
      type: "provider_action",
      name: "Generate image",
      config: { capability: "image_generation" },
      inputs: [{ port: "prompt", type: "prompt" }],
      outputs: [{ port: "image", type: "image" }],
    },
  ],
  edges: [{ id: "e1", from_step: "take", from_port: "prompt", to_step: "gen", to_port: "prompt" }],
  ui: {},
};

// v2 adds an instruction step "notes" — used for the diff + upgrade flow
const DEF_A_V2 = {
  ...DEF_A_V1,
  steps: [
    ...DEF_A_V1.steps,
    {
      id: "notes",
      type: "instruction",
      name: "Review Notes",
      config: { content: "Check the generated image against the brand kit" },
      inputs: [],
      outputs: [],
    },
  ],
};

const DEF_B = {
  schema_version: 1,
  inputs: [{ key: "prompt", type: "prompt", label: "Prompt", required: true }],
  outputs: [{ key: "clip", type: "video", from_step: "vid", from_port: "video" }],
  steps: [
    {
      id: "take",
      type: "asset_input",
      name: "Take prompt",
      config: {},
      inputs: [],
      outputs: [{ port: "prompt", type: "prompt" }],
    },
    {
      id: "vid",
      type: "provider_action",
      name: "Make video",
      config: { capability: "text_to_video" },
      inputs: [{ port: "prompt", type: "prompt" }],
      outputs: [{ port: "video", type: "video" }],
    },
  ],
  edges: [{ id: "e1", from_step: "take", from_port: "prompt", to_step: "vid", to_port: "prompt" }],
  ui: {},
};

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("Providers Sweep Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  orgId = await createOrg(admin, `ProvSweep-${Date.now()}`);

  // Seed pack A (satisfiable) — definition v1 + release 1.0.0
  const packA = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `Sweep ImgGen ${Date.now()}`,
  });
  packAId = packA.body.data.id;
  const defA = await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${packAId}/definition`, {
    definition: DEF_A_V1,
  });
  expect(defA.status).toBe(200);
  const relA = await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packAId}/releases`, {
    version: "1.0.0",
  });
  expect(relA.status).toBe(201);

  // Seed pack B (capability gap: text_to_video has no offering in this org)
  const packB = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `Sweep Gap ${Date.now()}`,
  });
  packBId = packB.body.data.id;
  const defB = await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${packBId}/definition`, {
    definition: DEF_B,
  });
  expect(defB.status).toBe(200);
  const relB = await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packBId}/releases`, {
    version: "1.0.0",
  });
  expect(relB.status).toBe(201);

  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

// ─────────────────────────────────────────────────────────────────────────────

test("providers: empty state → create mock connection via UI", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");

  // Empty state before any connection exists
  await expect(page.getByText("No provider connections yet.")).toBeVisible();

  // Create the mock connection through the form
  await page.getByLabel("Provider adapter").selectOption({ label: "Mock Provider" });
  await page.getByPlaceholder("Connection name").fill(MOCK_CONN);
  await page.getByRole("button", { name: "Connect", exact: true }).click();

  // Card renders with name, adapter label, and active status badge
  const card = page.locator("div.rounded-lg.border.p-4").filter({ hasText: MOCK_CONN });
  await expect(card).toBeVisible({ timeout: 10_000 });
  await expect(card.getByText("active")).toBeVisible();
  // Mock adapter declares no credential fields → no lock indicator
  await expect(card.getByText("credentials stored")).toHaveCount(0);
  // Empty state gone
  await expect(page.getByText("No provider connections yet.")).toHaveCount(0);
});

test("providers: add offering via UI form; client + server validation", async () => {
  // Client-side gating: Add Offering stays disabled until model name is filled
  await page.getByLabel("Connection", { exact: true }).selectOption({ label: MOCK_CONN });
  await page.getByLabel("Capability", { exact: true }).selectOption("image_generation");
  await expect(page.getByRole("button", { name: "Add Offering" })).toBeDisabled();

  await page.getByPlaceholder("Model name").fill(MODEL);
  await page.getByLabel("Quality tier").selectOption("premium");
  await page.getByRole("button", { name: "Add Offering" }).click();

  // Offering renders inside the connection card's table
  const card = page.locator("div.rounded-lg.border.p-4").filter({ hasText: MOCK_CONN });
  await expect(card.getByText("image_generation")).toBeVisible({ timeout: 10_000 });
  await expect(card.getByText(MODEL)).toBeVisible();
  await expect(card.getByText("premium")).toBeVisible();
  await expect(card.getByText("✓")).toBeVisible();

  // Server-side validation for negative cost — the UI form exposes no cost
  // field (see APP BUGS in report), so the 422 contract is asserted via API.
  const conns = await api(admin, "GET", `/orgs/${orgId}/provider-connections`);
  const connId = conns.body.data.find((c: { name: string }) => c.name === MOCK_CONN).id;
  const neg = await api(admin, "POST", `/orgs/${orgId}/provider-offerings`, {
    connection_id: connId,
    capability_key: "image_generation",
    model_name: "neg-cost",
    cost_per_call_usd: -5,
  });
  expect(neg.status).toBe(422);
  expect(neg.body.error.code).toBe("VALIDATION_ERROR");
  expect(neg.body.error.message).toContain("Cost must be between 0 and 10,000");

  // Remember the UI-created offering id for binding assertions later
  const offs = await api(admin, "GET", `/orgs/${orgId}/provider-offerings`);
  offeringId = offs.body.data.find((o: { model_name: string }) => o.model_name === MODEL).id;
  expect(offeringId).toBeTruthy();
});

test("credentials: write-only api_key never appears in DOM; delete connection via UI", async () => {
  // Anthropic adapter declares credential field "api_key"
  await page.getByLabel("Provider adapter").selectOption({ label: "Anthropic" });
  const credInput = page.locator("#cred-api_key");
  await expect(credInput).toBeVisible();
  await expect(credInput).toHaveAttribute("type", "password");
  await expect(page.getByText("Stored encrypted; never shown again.")).toBeVisible();

  await page.getByPlaceholder("Connection name").fill(ANTHROPIC_CONN);
  await credInput.fill(SECRET);
  await page.getByRole("button", { name: "Connect", exact: true }).click();

  const card = page.locator("div.rounded-lg.border.p-4").filter({ hasText: ANTHROPIC_CONN });
  await expect(card).toBeVisible({ timeout: 10_000 });
  // Lock indicator proves a credential_id round-tripped — value must not
  await expect(card.getByText("credentials stored")).toBeVisible();

  // The secret must never appear anywhere in the DOM after save
  const htmlAfterSave = await page.content();
  expect(htmlAfterSave).not.toContain(SECRET);

  // ... nor after a full reload (fresh GETs for connections/adapters)
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(
    page.locator("div.rounded-lg.border.p-4").filter({ hasText: ANTHROPIC_CONN }),
  ).toBeVisible();
  const htmlAfterReload = await page.content();
  expect(htmlAfterReload).not.toContain(SECRET);

  // Delete the anthropic connection via the armed two-click flow
  const freshCard = page.locator("div.rounded-lg.border.p-4").filter({ hasText: ANTHROPIC_CONN });
  await freshCard.getByRole("button", { name: "Delete", exact: true }).click();
  await freshCard.getByRole("button", { name: "Confirm delete?" }).click();
  await expect(page.getByText(ANTHROPIC_CONN)).toHaveCount(0, { timeout: 10_000 });
  // Mock connection untouched (scoped to its card — the name also appears
  // as an <option> in the offering form's connection select)
  await expect(
    page.locator("div.rounded-lg.border.p-4").filter({ hasText: MOCK_CONN }),
  ).toBeVisible();
});

test("installations: empty state → install (API) → bindings render → confirm via UI", async () => {
  // Empty state before anything is installed
  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("No workflow packs installed yet.")).toBeVisible();

  // Seed the install via API (capability gate satisfied by the UI-made offering)
  const inst = await api(admin, "POST", `/orgs/${orgId}/workflow-installations`, {
    pack_id: packAId,
    version: "1.0.0",
  });
  expect(inst.status).toBe(201);
  installAId = inst.body.data.id;

  // List renders the installation with version + status badge
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("v1.0.0")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("active", { exact: true })).toBeVisible();

  // Navigate to the detail via the list link
  await page.locator(`a[href$="/workflow-installations/${installAId}"]`).click();
  await page.waitForURL(new RegExp(`workflow-installations/${installAId}$`), {
    timeout: 10_000,
  });
  await page.waitForLoadState("networkidle");

  // Bindings section: one provider_action step "gen", auto-suggested offering
  await expect(page.getByText("Provider Bindings")).toBeVisible();
  await expect(page.getByText("gen", { exact: true })).toBeVisible();
  await expect(page.getByText("suggested")).toBeVisible();
  const offeringSelect = page.getByLabel("Offering for gen");
  await expect(offeringSelect).toHaveValue(offeringId);

  // Change binding mode, then confirm the binding
  await page.getByLabel("Binding mode for gen").selectOption("pinned");
  await page.getByRole("button", { name: "Confirm", exact: true }).click();
  await expect(page.getByText("Binding confirmed")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("confirmed", { exact: true })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("suggested")).toHaveCount(0);
});

test("upgrade: diff viewer + upgrade to 1.1.0 via UI; confirmed binding preserved", async () => {
  // Publish 1.1.0 via API (adds instruction step "notes")
  const def2 = await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${packAId}/definition`, {
    definition: DEF_A_V2,
  });
  expect(def2.status).toBe(200);
  const rel2 = await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packAId}/releases`, {
    version: "1.1.0",
  });
  expect(rel2.status).toBe(201);

  // Diff viewer: compare current 1.0.0 with 1.1.0
  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations/${installAId}`);
  await page.waitForLoadState("networkidle");
  await page.locator("#diff-version").fill("1.1.0");
  await page.getByRole("button", { name: "Show Diff" }).click();
  await expect(page.getByText("Added: notes")).toBeVisible({ timeout: 10_000 });

  // Upgrade via the #upgrade-version input
  await page.locator("#upgrade-version").fill("1.1.0");
  await page.getByRole("button", { name: "Apply", exact: true }).click();
  await expect(page.getByText("Installation updated")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(/v1\.1\.0/)).toBeVisible({ timeout: 10_000 });

  // The human-confirmed binding for "gen" survived the upgrade (D5)
  await expect(page.getByText("confirmed", { exact: true })).toBeVisible({ timeout: 10_000 });
});

test("unhappy: upgrade to capability-gated 1.2.0 shows CAPABILITY_UNSATISFIED in UI", async () => {
  // Publish 1.2.0 declaring a capability this org cannot satisfy
  const rel3 = await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${packAId}/releases`, {
    version: "1.2.0",
    dependencies: { requires_capabilities: [{ capability: "voice_generation" }] },
  });
  expect(rel3.status).toBe(201);

  await page.locator("#upgrade-version").fill("1.2.0");
  await page.getByRole("button", { name: "Apply", exact: true }).click();

  // The 422 CAPABILITY_UNSATISFIED message surfaces as an error toast
  await expect(
    page.getByText("Organization is missing required provider capabilities for this workflow"),
  ).toBeVisible({ timeout: 10_000 });
  // Version unchanged
  await expect(page.getByText(/v1\.1\.0/)).toBeVisible();
});

test("unhappy: binding gap (no offering for capability) rendered; confirm disabled", async () => {
  // Install pack B — its provider_action needs text_to_video (no offering)
  const inst = await api(admin, "POST", `/orgs/${orgId}/workflow-installations`, {
    pack_id: packBId,
  });
  expect(inst.status).toBe(201);
  installBId = inst.body.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations/${installBId}`);
  await page.waitForLoadState("networkidle");

  // Binding row for step "vid" is a suggestion with a red gap message
  await expect(page.getByText("vid", { exact: true })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("suggested")).toBeVisible();
  await expect(page.getByText("No active offering for 'text_to_video'")).toBeVisible();
  // No offering selected → Confirm is disabled
  await expect(page.getByLabel("Offering for vid")).toHaveValue("");
  await expect(page.getByRole("button", { name: "Confirm", exact: true })).toBeDisabled();
});

test("runs list: empty state → 2 seeded runs render with terminal statuses", async () => {
  test.setTimeout(90_000);

  // Empty state before any run exists
  await page.goto(`/dashboard/orgs/${orgId}/workflow-runs`);
  await page.waitForLoadState("networkidle");
  await expect(
    page.getByText("No workflow runs yet. Start one from an installation."),
  ).toBeVisible();

  // Seed two runs via API: one completes (mock offering), one fails (gap)
  const run1 = await api(admin, "POST", `/orgs/${orgId}/workflow-runs`, {
    installation_id: installAId,
    inputs: { prompt: "sweep run one" },
  });
  expect(run1.status).toBe(201);
  runCompletedId = run1.body.data.id;
  const run2 = await api(admin, "POST", `/orgs/${orgId}/workflow-runs`, {
    installation_id: installBId,
    inputs: { prompt: "sweep run two" },
  });
  expect(run2.status).toBe(201);
  runFailedId = run2.body.data.id;

  // Wait (via API) until both reach terminal statuses, then assert the UI
  await expect
    .poll(
      async () => {
        const r = await api(admin, "GET", `/orgs/${orgId}/workflow-runs/${runCompletedId}`);
        return r.body.data.status;
      },
      { timeout: 30_000 },
    )
    .toBe("completed");
  await expect
    .poll(
      async () => {
        const r = await api(admin, "GET", `/orgs/${orgId}/workflow-runs/${runFailedId}`);
        return r.body.data.status;
      },
      { timeout: 30_000 },
    )
    .toBe("failed");

  await page.reload();
  await page.waitForLoadState("networkidle");

  const row1 = page.locator(`a[href$="/workflow-runs/${runCompletedId}"]`);
  await expect(row1).toBeVisible({ timeout: 10_000 });
  await expect(row1.getByText(runCompletedId)).toBeVisible();
  await expect(row1.getByText("completed")).toBeVisible();

  const row2 = page.locator(`a[href$="/workflow-runs/${runFailedId}"]`);
  await expect(row2).toBeVisible();
  await expect(row2.getByText("failed", { exact: true })).toBeVisible();
  // Failed run surfaces its error code in the row subtitle
  await expect(row2.getByText(/WF_STEP_FAILED/)).toBeVisible();

  // Pagination controls only render when total > 20 — with 2 runs: absent
  // (exact: the Next.js dev-tools overlay button matches a bare "Next")
  await expect(page.getByRole("button", { name: "Previous", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Next", exact: true })).toHaveCount(0);
});

test("uninstall via UI: remove pack B installation", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations/${installBId}`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("button", { name: "Remove", exact: true })).toBeVisible();

  page.once("dialog", (d) => d.accept());
  await page.getByRole("button", { name: "Remove", exact: true }).click();

  // onSuccess router.replaces back to the list
  await page.waitForURL(/workflow-installations$/, { timeout: 10_000 });
  await page.waitForLoadState("networkidle");
  // Pack B gone from the list; pack A still installed
  await expect(page.getByText(packBId)).toHaveCount(0);
  await expect(page.locator(`a[href$="/workflow-installations/${installAId}"]`)).toBeVisible();
});

test("providers: delete mock connection via UI cascades offerings", async () => {
  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");

  const card = page.locator("div.rounded-lg.border.p-4").filter({ hasText: MOCK_CONN });
  await expect(card).toBeVisible();
  // Cancel path of the armed delete first
  await card.getByRole("button", { name: "Delete", exact: true }).click();
  await card.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(card.getByRole("button", { name: "Confirm delete?" })).toHaveCount(0);
  // Now actually delete
  await card.getByRole("button", { name: "Delete", exact: true }).click();
  await card.getByRole("button", { name: "Confirm delete?" }).click();

  // Both connection and its cascaded offering disappear; empty state returns
  await expect(page.getByText("No provider connections yet.")).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByText(MOCK_CONN)).toHaveCount(0);
  await expect(page.getByText(MODEL)).toHaveCount(0);
});

test("unhappy: student role cannot create provider connection (403 shown in UI)", async () => {
  // Register a student and add them to the org via API
  const student = await registerUser("Providers Sweep Student");
  await addOrgMember(admin, orgId, student.userId, "student");

  // Log in AS the student in the same browser context
  await loginInBrowser(page, student.email, "TestPass123!");
  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");

  // Student can read the page (member) but the create must be denied
  await expect(page.getByText("No provider connections yet.")).toBeVisible();
  await page.getByLabel("Provider adapter").selectOption({ label: "Mock Provider" });
  await page.getByPlaceholder("Connection name").fill("Student Conn");
  await page.getByRole("button", { name: "Connect", exact: true }).click();

  // 403 "Insufficient org permissions" surfaces as an error toast
  await expect(page.getByText("Insufficient org permissions")).toBeVisible({
    timeout: 10_000,
  });
  // And nothing was created
  await expect(page.getByText("Student Conn")).toHaveCount(0);
});
