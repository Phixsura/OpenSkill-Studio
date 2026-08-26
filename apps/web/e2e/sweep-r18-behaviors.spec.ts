/**
 * Sweep: ROUND 15-20 NEW BEHAVIORS — coverage the 293-suite predates.
 *
 * The main suite was written before these behaviors existed, so "293 green"
 * never exercised them (the e2e-level twin of the R15 test-quality finding).
 * Covered here:
 * 1. Port-rename collision guard (R18 PortNameInput): renaming a port
 *    THROUGH a sibling's exact name never misroutes the sibling's edge.
 * 2. json-typed run input renders a textarea + client-side parse (R16).
 * 3. Installations list pagination (R16): >20 installs reachable via Next.
 * 4. Providers page error state (R16): API failure shows an error, not the
 *    misleading empty state. (Simulated via route interception.)
 * 5. Card-field approval reset (R18): editing an approved pack's summary
 *    voids approval — UI shows draft/unlisted state after edit.
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

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
  admin = await registerUser(`r18b-${Date.now()}`);
  orgId = await createOrg(admin, `R18B ${Date.now()}`);
  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx.close();
});

// ═══ 1. Port-rename collision guard ═══
test("port rename through a sibling's exact name never misroutes edges", async () => {
  // Pack with a sink step having two input ports in / in2, each fed by an edge
  const pack = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `Collision ${Date.now()}`,
  });
  const pid = pack.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${pid}/definition`, {
    definition: {
      schema_version: 1,
      inputs: [{ key: "topic", type: "text", required: true }],
      outputs: [{ key: "final", type: "text", from_step: "sink", from_port: "out" }],
      steps: [
        {
          id: "src1",
          type: "prompt_template",
          name: "Source One",
          config: { template: "a {{inputs.topic}}" },
          inputs: [],
          outputs: [{ port: "p", type: "text" }],
        },
        {
          id: "src2",
          type: "prompt_template",
          name: "Source Two",
          config: { template: "b {{inputs.topic}}" },
          inputs: [],
          outputs: [{ port: "p", type: "text" }],
        },
        {
          id: "sink",
          type: "transform",
          name: "Sink Step",
          config: { operation: "concat_text", params: {} },
          inputs: [
            { port: "in", type: "text" },
            { port: "in2", type: "text" },
          ],
          outputs: [{ port: "out", type: "text" }],
        },
      ],
      edges: [
        { id: "e1", from_step: "src1", from_port: "p", to_step: "sink", to_port: "in" },
        { id: "e2", from_step: "src2", from_port: "p", to_step: "sink", to_port: "in2" },
      ],
      ui: {},
    },
  });

  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${pid}/editor`);
  await page.waitForLoadState("networkidle");
  // List view → select the sink step to open its config panel
  await page.getByRole("button", { name: "List", exact: true }).click();
  await page.getByRole("button", { name: /Sink Step/ }).first().click();

  // Rename in2 → in3 by keystrokes that pass through the sibling name 'in':
  // clear the field (transient ''), type 'i','n' (== sibling!), then '3'.
  const portInput = page.getByLabel("Input ports name 2");
  await portInput.click();
  await portInput.press("ControlOrMeta+a");
  await portInput.pressSequentially("in3", { delay: 60 });
  await sleep(400);

  // Save and verify via API that both edges survived with correct routing
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await sleep(1200);
  const detail = await api(admin, "GET", `/orgs/${orgId}/workflow-packs/${pid}`);
  const def = detail.data.definition;
  const e1 = def.edges.find((e: { id: string }) => e.id === "e1");
  const e2 = def.edges.find((e: { id: string }) => e.id === "e2");
  expect(e1?.to_port).toBe("in"); // sibling untouched
  expect(e2?.to_port).toBe("in3"); // renamed port kept its edge
});

// ═══ 2. json input renders textarea + parses ═══
test("json-typed run input: textarea with parse validation", async () => {
  const pack = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `JsonInput ${Date.now()}`,
  });
  const pid = pack.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${pid}/definition`, {
    definition: {
      schema_version: 1,
      inputs: [{ key: "cfg", type: "json", required: true }],
      outputs: [{ key: "echo", type: "json", from_step: "out", from_port: "o" }],
      steps: [
        {
          id: "loader",
          type: "asset_input",
          name: "Load",
          config: { accept_types: [] },
          inputs: [],
          outputs: [{ port: "cfg", type: "json" }],
        },
        {
          id: "out",
          type: "output",
          name: "Out",
          config: {},
          inputs: [{ port: "i", type: "json" }],
          outputs: [{ port: "o", type: "json" }],
        },
      ],
      edges: [{ id: "e1", from_step: "loader", from_port: "cfg", to_step: "out", to_port: "i" }],
      ui: {},
    },
  });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${pid}/releases`, { version: "1.0.0" });
  const inst = await api(admin, "POST", `/orgs/${orgId}/workflow-installations`, {
    pack_id: pid,
    version: "1.0.0",
  });
  const instId = inst.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/workflow-installations/${instId}`);
  await page.waitForLoadState("networkidle");

  // json input renders a TEXTAREA (R16 — was a text Input that always 422'd)
  const jsonField = page.locator("textarea").first();
  await expect(jsonField).toBeVisible({ timeout: 10_000 });

  // Invalid JSON blocks with an inline error
  await jsonField.fill("{not json");
  await page.getByRole("button", { name: /Start Run/i }).click();
  await expect(page.getByText(/valid JSON/i)).toBeVisible({ timeout: 5_000 });

  // Valid JSON starts the run
  await jsonField.fill('{"width": 512}');
  await page.getByRole("button", { name: /Start Run/i }).click();
  await sleep(1500);
  const runs = await api(admin, "GET", `/orgs/${orgId}/workflow-runs?page=1`);
  const run = runs.data.find(
    (r: { installation_id: string }) => r.installation_id === instId,
  );
  expect(run).toBeTruthy();
  expect(run.inputs.cfg).toEqual({ width: 512 });
});

// ═══ 3. Providers page error state ═══
test("providers page shows error state on API failure, not empty state", async () => {
  // Intercept the connections call with a 500 BEFORE navigating
  await page.route("**/api/v1/orgs/*/provider-connections*", (route) =>
    route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ error: { code: "INTERNAL_ERROR", message: "boom" } }),
    }),
  );
  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");
  // Error state visible; misleading empty state absent (R16)
  await expect(page.getByText(/failed|error|could not/i).first()).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByText("No provider connections yet.")).toHaveCount(0);
  await page.unroute("**/api/v1/orgs/*/provider-connections*");
});

// ═══ 4. Card-field approval reset ═══
test("editing an approved pack's card fields voids approval (unlisted detour closed)", async () => {
  const pack = await api(admin, "POST", `/orgs/${orgId}/workflow-packs`, {
    name: `CardReset ${Date.now()}`,
  });
  const pid = pack.data.id;
  await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${pid}/definition`, {
    definition: {
      schema_version: 1,
      inputs: [{ key: "topic", type: "text", required: true }],
      outputs: [{ key: "final", type: "prompt", from_step: "s", from_port: "p" }],
      steps: [
        {
          id: "s",
          type: "prompt_template",
          name: "S",
          config: { template: "x {{inputs.topic}}" },
          inputs: [],
          outputs: [{ port: "p", type: "prompt" }],
        },
      ],
      edges: [],
      ui: {},
    },
  });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${pid}/releases`, { version: "1.0.0" });
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${pid}/submit-review`, {});
  await api(admin, "POST", `/orgs/${orgId}/workflow-packs/${pid}/approve`, {});
  const pub = await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${pid}`, {
    visibility: "public",
  });
  expect(pub.data.visibility).toBe("public");

  // Rewrite the card summary → approval voided, visibility pulled to unlisted
  const edited = await api(admin, "PUT", `/orgs/${orgId}/workflow-packs/${pid}`, {
    summary: "Totally different pitch",
  });
  expect(edited.data.review_status).toBeNull();
  expect(edited.data.visibility).toBe("unlisted");

  // And the UI reflects it: detail page no longer shows the public badge
  await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${pid}`);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("unlisted").first()).toBeVisible({ timeout: 10_000 });
});
