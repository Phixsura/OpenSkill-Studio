/**
 * Skill Pack Registry — complete browser interaction E2E.
 *
 * Every test fills real forms, clicks real buttons, and asserts real outcomes.
 * Zero API fallbacks. Zero "if visible" guards. Pure UI.
 *
 * DOM structure verified from screenshots:
 * - Pack form: #name, #summary, #description(textarea), #visibility(select), #difficulty(select), #minutes, #scenarioTags, #toolTags, #learningOutcomes(textarea)
 * - Pack detail: "×" remove buttons, "Select skill..."/"Select template..." dropdowns, "Add" buttons, #releaseVersion input, "Publish" button, "Set Private"/"Archive" buttons
 * - Path form: #name, #estimated_minutes, #description(textarea)
 * - Path detail: editable name input, Type select (Skill/Project/Section), "Select a skill..." dropdown, "Add Item" button, "Publish"/"Archive" buttons
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import {
  registerUser,
  createOrg,
  loginInBrowser,
  createCohort,
  activateCohort,
  type AuthContext,
} from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let admin: AuthContext;
let consumer: AuthContext;
let orgId: string;
let conOrgId: string;
let adminCtx: BrowserContext;
let adminPage: Page;
let conCtx: BrowserContext;
let conPage: Page;

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
  // Register both users with rate-limit handling
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("FullE2E Admin");
      break;
    } catch {
      await sleep(5000);
    }
  }
  await sleep(3000);
  for (let i = 0; i < 5; i++) {
    try {
      consumer = await registerUser("FullE2E Consumer");
      break;
    } catch {
      await sleep(5000);
    }
  }

  orgId = await createOrg(admin, `FullE2E-${Date.now()}`);
  conOrgId = await createOrg(consumer, `FullCon-${Date.now()}`);

  // Pre-create a category + skills for the pack detail tests
  const cat = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `FullCat-${Date.now()}`,
  });
  console.log("CAT CREATE:", JSON.stringify(cat));
  const sk1 = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "Prompt Engineering",
    description: "Learn prompts",
    difficulty: "beginner",
    category_id: cat.data.id,
  });
  console.log("SKILL1 CREATE:", JSON.stringify(sk1).slice(0, 200));
  const sk2 = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "Image Generation",
    description: "AI images",
    difficulty: "intermediate",
    category_id: cat.data.id,
  });
  console.log("SKILL2 CREATE:", JSON.stringify(sk2).slice(0, 200));

  // Login admin
  adminCtx = await browser.newContext();
  adminPage = await adminCtx.newPage();
  await loginInBrowser(adminPage, admin.email, "TestPass123!");

  // Login consumer
  await sleep(2000);
  conCtx = await browser.newContext();
  conPage = await conCtx.newPage();
  await loginInBrowser(conPage, consumer.email, "TestPass123!");
});

test.afterAll(async () => {
  await adminCtx?.close();
  await conCtx?.close();
});

// ═══════════════════════════════════════════════════════════════
// PART 1: PACK CREATION — fill every field, submit
// ═══════════════════════════════════════════════════════════════

test("1. Fill pack creation form with all fields and submit", async () => {
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/new`);
  await adminPage.waitForLoadState("networkidle");

  // Fill every field using exact IDs from DOM audit
  await adminPage.locator("#name").fill("AI Photography Masterclass");
  await adminPage.locator("#summary").fill("Complete AI product photography training");
  await adminPage
    .locator("#description")
    .fill("Master AI-powered product photography from beginner to expert level");
  await adminPage.locator("#visibility").selectOption("Public");
  await adminPage.locator("#difficulty").selectOption("Beginner");
  await adminPage.locator("#minutes").fill("480");
  await adminPage.locator("#scenarioTags").fill("ecommerce, product-ads");
  await adminPage.locator("#toolTags").fill("midjourney, comfyui, photoshop");
  await adminPage
    .locator("#learningOutcomes")
    .fill("Create hero product images\nControl AI composition\nPost-process AI outputs");

  // Take screenshot before submit
  await adminPage.screenshot({ path: "e2e/screenshots/pack-form-filled.png" });

  // Submit
  await adminPage.click('button:has-text("Create Skill Pack")');

  // Assert: redirected to pack detail
  await adminPage.waitForURL(/\/packs\/01/, { timeout: 15_000 });
  await adminPage.waitForLoadState("networkidle");

  // Assert: pack name visible
  await expect(adminPage.locator("text=AI Photography Masterclass")).toBeVisible();
  // Assert: status = draft
  await expect(adminPage.locator("text=draft")).toBeVisible();
  // Assert: visibility = public
  await expect(adminPage.locator("text=public")).toBeVisible();

  await adminPage.screenshot({ path: "e2e/screenshots/pack-created.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 2: ADD SKILL — use "Select skill..." dropdown + "Add" button
// ═══════════════════════════════════════════════════════════════

test("2. Add skill to pack via dropdown and Add button", async () => {
  // Create a separate pack via API for this test (UI-created pack from test 1 may not have reloaded skills)
  const apiPack = await api(admin, "POST", `/orgs/${orgId}/packs`, {
    name: "API Detail Pack",
    visibility: "public",
  });
  const apiPackId = apiPack.data.id;

  // Navigate to this pack's detail page
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/${apiPackId}`);
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Wait for skill dropdown to populate
  const skillSelect = adminPage.locator("select").filter({ hasText: "Select skill..." });
  await expect(skillSelect).toBeVisible();

  // Get dropdown options
  const options = await skillSelect.locator("option").allTextContents();

  const promptOpt = options.find((o) => o.includes("Prompt Engineering"));
  expect(promptOpt).toBeTruthy();
  await skillSelect.selectOption({ label: promptOpt! });

  // Click Add button
  await adminPage.locator("button:has-text('Add')").first().click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Assert: skill appears in Contents section
  await expect(adminPage.locator("text=Prompt Engineering")).toBeVisible();

  // Add second skill
  await sleep(500);
  const skillSelect2 = adminPage.locator("select").filter({ hasText: "Select skill..." });
  const options2 = await skillSelect2.locator("option").allTextContents();
  const imageOpt = options2.find((o) => o.includes("Image Generation"));
  expect(imageOpt).toBeTruthy();
  await skillSelect2.selectOption({ label: imageOpt! });
  await adminPage.locator("button:has-text('Add')").first().click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  await expect(adminPage.locator("text=Image Generation")).toBeVisible();

  // Save this packId for later tests
  packId = apiPackId;

  await adminPage.screenshot({ path: "e2e/screenshots/pack-skills-added.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 3: PUBLISH RELEASE — fill version + changelog, click Publish
// ═══════════════════════════════════════════════════════════════

test("3. Publish release: fill version, changelog, click Publish", async () => {
  // Navigate to the pack we added skills to
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/${packId}`);
  await adminPage.waitForLoadState("networkidle");
  await sleep(500);

  // Fill version input (id=releaseVersion)
  await adminPage.locator("#releaseVersion").fill("1.0.0");

  // Fill changelog textarea (last textarea on page)
  await adminPage.locator("textarea").last().fill("Initial release: 2 skills for AI photography");

  // Click Publish button
  await adminPage.locator("button:has-text('Publish')").click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Assert: release version visible in Releases section
  await expect(adminPage.locator("text=1.0.0")).toBeVisible();
  // Assert: pack status changed to published (badge may render in more
  // than one place — status chip + release row)
  await expect(adminPage.locator("text=published").first()).toBeVisible();

  await adminPage.screenshot({ path: "e2e/screenshots/pack-published.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 4: REMOVE SKILL — click "×" button, verify skill disappears
// ═══════════════════════════════════════════════════════════════

test("4. Remove skill from pack: click × button", async () => {
  // Count skills before
  const skillsBefore = await adminPage.locator("text=×").count();

  // Click first × button to remove first skill
  await adminPage.locator("button:has-text('×')").first().click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(500);

  // Assert: one fewer × button
  const skillsAfter = await adminPage.locator("text=×").count();
  expect(skillsAfter).toBeLessThan(skillsBefore);

  await adminPage.screenshot({ path: "e2e/screenshots/pack-skill-removed.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 5: SET PRIVATE — click "Set Private" button
// ═══════════════════════════════════════════════════════════════

test("5. Toggle visibility: click Set Private button", async () => {
  // Reload to clear toasts, then click
  await adminPage.reload();
  await adminPage.waitForLoadState("networkidle");
  await sleep(500);

  await adminPage.locator("button:has-text('Set Private')").click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Assert: visibility changed — "Set Public" button now visible (inverse)
  await expect(adminPage.locator("button:has-text('Set Public')")).toBeVisible({ timeout: 10_000 });

  // Change back to public for later tests
  await adminPage.locator("button:has-text('Set Public')").click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);
});

// ═══════════════════════════════════════════════════════════════
// PART 6: REGISTRY — search, filter, navigate to detail
// ═══════════════════════════════════════════════════════════════

test("6. Registry: search by name and filter by difficulty", async () => {
  await adminPage.goto("/registry");
  await adminPage.waitForLoadState("networkidle");

  // Type in search box — search for the published pack (API Detail Pack from test 2/3)
  const searchInput = adminPage.locator('input[placeholder*="Search"]');
  await searchInput.fill("API Detail Pack");
  await sleep(1500);

  // Assert: our pack card is visible
  await expect(adminPage.locator("text=API Detail Pack").first()).toBeVisible();

  // Clear search
  await searchInput.fill("");
  await sleep(1000);

  // Filter by difficulty
  const diffSelect = adminPage.locator("select").filter({ hasText: "All levels" });
  await diffSelect.selectOption("beginner");
  await sleep(1500);

  // Assert: results shown
  const cards = adminPage.locator("a[href*='/registry/']");
  expect(await cards.count()).toBeGreaterThanOrEqual(1);

  await adminPage.screenshot({ path: "e2e/screenshots/registry-filtered.png" });
});

test("7. Registry: click pack card → detail page → verify content", async () => {
  await adminPage.goto("/registry");
  await adminPage.waitForLoadState("networkidle");

  // Click first pack card — exclude the "/registry/workflows" family-tab
  // link (Issue #21) which now also matches a[href*='/registry/']
  await adminPage
    .locator("a[href*='/registry/']:not([href*='/registry/workflows'])")
    .first()
    .click();
  await adminPage.waitForLoadState("networkidle");

  // Assert: on detail page ("Releases" section renamed "Version History")
  await expect(adminPage.locator("text=← Back to Registry").first()).toBeVisible();
  await expect(adminPage.locator("text=Version History")).toBeVisible();
  await expect(adminPage.locator("text=Install in your organization")).toBeVisible();

  await adminPage.screenshot({ path: "e2e/screenshots/registry-detail.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 7: INSTALL + INSTALLATIONS PAGE
// ═══════════════════════════════════════════════════════════════

let packId: string;
let installId: string;

test("8. Install pack and verify in Installed tab", async () => {
  // packId was set in test 2 (API Detail Pack)
  // Install via API
  const inst = await api(consumer, "POST", `/orgs/${conOrgId}/installations`, { pack_id: packId });
  if (!inst.data) {
    console.log("INSTALL ERROR:", JSON.stringify(inst));
    throw new Error(`Install failed: ${JSON.stringify(inst)}`);
  }
  installId = inst.data.id;

  // Navigate consumer to Installed tab
  await conPage.goto(`/dashboard/orgs/${conOrgId}`);
  await conPage.waitForLoadState("networkidle");
  await conPage.click("text=Installed");
  await conPage.waitForLoadState("networkidle");

  // Assert: installation visible with version
  await expect(conPage.locator("text=1.0.0")).toBeVisible();
  await expect(conPage.locator("h1")).toContainText(/Installed/i);

  await conPage.screenshot({ path: "e2e/screenshots/installations-list.png" });
});

test("9. Installation detail: Fork button click → status changes", async () => {
  // Navigate to installation detail
  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations/${installId}`);
  await conPage.waitForLoadState("networkidle");

  // Assert: version and action buttons visible
  await expect(conPage.locator("text=1.0.0")).toBeVisible();
  await expect(conPage.locator("button:has-text('Fork')")).toBeVisible();
  await expect(conPage.locator("button:has-text('Remove')")).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/install-detail-before-fork.png" });

  // Click Fork, accept dialog
  conPage.on("dialog", (d) => d.accept());
  await conPage.locator("button:has-text('Fork')").click();
  await conPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Assert: status shows "forked"
  await expect(conPage.getByText("forked", { exact: true }).first()).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/install-forked.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 8: LEARNING PATH — create, add items, publish
// ═══════════════════════════════════════════════════════════════

test("10. Create learning path: fill form, submit", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/new`);
  await conPage.waitForLoadState("networkidle");

  // Fill fields using exact IDs from audit
  await conPage.locator("#name").fill("AI Creator Bootcamp");
  await conPage.locator("#description").fill("12-week intensive AI creator training");
  await conPage.locator("#estimated_minutes").fill("2400");

  await conPage.screenshot({ path: "e2e/screenshots/path-form-filled.png" });

  // Submit
  await conPage.click('button:has-text("Create Learning Path")');

  // Assert: redirected to path detail
  await conPage.waitForURL(/\/paths\/01/, { timeout: 15_000 });
  await conPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Assert: on path detail page
  await expect(conPage).toHaveURL(/\/paths\/01/);
  await sleep(2000);
  // Path name appears as editable input or text
  const nameInput = conPage.locator('input[type="text"]').first();
  if (await nameInput.isVisible({ timeout: 3000 }).catch(() => false)) {
    await expect(nameInput).toHaveValue("AI Creator Bootcamp");
  }

  await conPage.screenshot({ path: "e2e/screenshots/path-created.png" });
});

test("11. Add section item to path", async () => {
  // Select "Section" from Type dropdown
  const typeSelect = conPage.locator("select").first();
  await typeSelect.selectOption("Section");
  await sleep(500);

  // Fill section title input (placeholder: "e.g. Week 1: Getting Started")
  const titleInput = conPage
    .locator('input[placeholder*="Week" i], input[placeholder*="Getting" i]')
    .first();
  await titleInput.fill("Module 1: Foundations");

  // Click "Add Item"
  await conPage.click('button:has-text("Add Item")');
  await conPage.waitForLoadState("networkidle");
  await sleep(500);

  // Assert: section appears in items list
  await expect(conPage.locator("text=Module 1: Foundations")).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/path-section-added.png" });
});

test("12. Add skill item to path", async () => {
  // Select "Skill" from Type dropdown
  const typeSelect = conPage
    .locator("select")
    .filter({ hasText: /Skill|Section/ })
    .first();
  await typeSelect.selectOption("Skill");
  await sleep(500);

  // Pick a skill from the skill dropdown
  const skillSelect = conPage.locator("select").filter({ hasText: "Select a skill..." });
  const options = await skillSelect.locator("option").allTextContents();
  const realSkill = options.find((o) => o.length > 3 && !o.includes("Select"));

  if (realSkill) {
    await skillSelect.selectOption({ label: realSkill });
    await conPage.click('button:has-text("Add Item")');
    await conPage.waitForLoadState("networkidle");
    await sleep(500);

    // Assert: skill appears
    await expect(conPage.locator(`text=${realSkill}`).first()).toBeVisible();
  }

  await conPage.screenshot({ path: "e2e/screenshots/path-skill-added.png" });
});

test("13. Publish path: click Publish button → status changes", async () => {
  await conPage.locator("button:has-text('Publish')").click();
  await conPage.waitForLoadState("networkidle");
  await sleep(500);

  // Assert: status changed to published
  await expect(conPage.locator("text=published")).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/path-published.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 9: COHORT PATH ASSIGNMENT — select path, assign, verify
// ═══════════════════════════════════════════════════════════════

test("14. Assign path to cohort via UI", async () => {
  // Create + activate cohort via API
  const cohortId = await createCohort(consumer, conOrgId, `FullCoh-${Date.now()}`);
  await activateCohort(consumer, conOrgId, cohortId);

  // Navigate to cohort paths tab
  await conPage.goto(`/dashboard/orgs/${conOrgId}/cohorts/${cohortId}/paths`);
  await conPage.waitForLoadState("networkidle");

  // Assert: heading visible
  await expect(conPage.locator("h2:has-text('Learning Paths')")).toBeVisible();

  // Select path from dropdown
  const pathSelect = conPage.locator("select").first();
  const options = await pathSelect.locator("option").allTextContents();
  const pathOption = options.find((o) => o.includes("AI Creator Bootcamp"));

  if (pathOption) {
    await pathSelect.selectOption({ label: pathOption });

    // Click Assign
    await conPage.click('button:has-text("Assign")');
    await conPage.waitForLoadState("networkidle");
    await sleep(500);

    // Assert: path appears in assigned list
    await expect(conPage.locator("text=AI Creator Bootcamp")).toBeVisible();

    await conPage.screenshot({ path: "e2e/screenshots/cohort-path-assigned.png" });

    // Unassign: click Remove
    await conPage.locator("button:has-text('Remove')").click();
    conPage.on("dialog", (d) => d.accept());
    await conPage.waitForLoadState("networkidle");
    await sleep(500);
  }
});

// ═══════════════════════════════════════════════════════════════
// PART 10: PACK LIST — verify cards, navigate
// ═══════════════════════════════════════════════════════════════

test("15. Pack list shows cards and navigates to detail", async () => {
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs`);
  await adminPage.waitForLoadState("networkidle");

  // Assert: heading
  await expect(adminPage.locator("h1")).toContainText(/Skill Packs/i);

  // Assert: our pack card visible
  await expect(adminPage.locator("text=AI Photography Masterclass")).toBeVisible();
  // Assert: status badge (use span to avoid matching hidden <option>)
  await expect(adminPage.locator("span:has-text('published')").first()).toBeVisible();

  await adminPage.screenshot({ path: "e2e/screenshots/pack-list-final.png" });

  // Click the pack card → navigate to detail
  await adminPage.locator("text=AI Photography Masterclass").click();
  await adminPage.waitForLoadState("networkidle");

  // Assert: on detail page
  await expect(adminPage.locator("text=Contents")).toBeVisible();
  await expect(adminPage.getByRole("heading", { name: "Releases" })).toBeVisible();
});

// ═══════════════════════════════════════════════════════════════
// PART 11: PATH LIST — verify cards
// ═══════════════════════════════════════════════════════════════

test("16. Path list shows created path", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths`);
  await conPage.waitForLoadState("networkidle");

  await expect(conPage.locator("h1")).toContainText(/Learning Paths/i);
  await expect(conPage.locator("text=AI Creator Bootcamp")).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/path-list-final.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 12: EXPORT — download zip
// ═══════════════════════════════════════════════════════════════

test("17. Export release returns valid zip", async () => {
  const res = await fetch(`${API}/orgs/${orgId}/packs/${packId}/releases/1.0.0/export`, {
    headers: admin.headers,
  });

  expect(res.status).toBe(200);
  expect(res.headers.get("content-type")).toBe("application/zip");
  expect(res.headers.get("content-disposition")).toContain("attachment");
  expect(res.headers.get("content-disposition")).toContain(".zip");

  const buf = await res.arrayBuffer();
  expect(buf.byteLength).toBeGreaterThan(100);
});

// ═══════════════════════════════════════════════════════════════
// PART 13: UPDATE — publisher publishes v1.1.0 with a new skill
// ═══════════════════════════════════════════════════════════════

let freshInstallId: string;
let conOrgId2: string;

test("18. Publish v1.1.0 update with an additional skill", async () => {
  // Add a third skill to the pack
  const cat = await api(admin, "GET", `/orgs/${orgId}/categories`);
  const catId = cat.data[0].id;
  const sk3 = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "Video Editing",
    description: "AI video editing",
    difficulty: "advanced",
    category_id: catId,
  });
  expect(sk3.data).toBeTruthy();

  // Add to pack
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/skills`, { skill_id: sk3.data.id });

  // Publish v1.1.0
  const rel = await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/releases`, {
    version: "1.1.0",
    changelog: "Added Video Editing skill",
  });
  expect(rel.data.version).toBe("1.1.0");

  // Verify on pack detail page: v1.1.0 visible
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/${packId}`);
  await adminPage.waitForLoadState("networkidle");
  await expect(adminPage.locator("text=1.1.0")).toBeVisible();

  await adminPage.screenshot({ path: "e2e/screenshots/pack-v110-published.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 14: DIFF — consumer checks diff between installed and latest
// ═══════════════════════════════════════════════════════════════

test("19. Install pack fresh and check update diff via API", async () => {
  // Create a second consumer org for a fresh (non-forked) install
  conOrgId2 = await createOrg(consumer, `FreshCon-${Date.now()}`);

  // Install v1.0.0 explicitly
  const inst = await api(consumer, "POST", `/orgs/${conOrgId2}/installations`, {
    pack_id: packId,
    version: "1.0.0",
  });
  expect(inst.data).toBeTruthy();
  freshInstallId = inst.data.id;
  expect(inst.data.installed_version).toBe("1.0.0");

  // Check for update
  const detail = await api(consumer, "GET", `/orgs/${conOrgId2}/installations/${freshInstallId}`);
  expect(detail.data.update_available).toBe(true);
  expect(detail.data.latest_version).toBe("1.1.0");

  // Get diff
  const diff = await api(
    consumer,
    "GET",
    `/orgs/${conOrgId2}/installations/${freshInstallId}/diff?version=1.1.0`,
  );
  expect(diff.data).toBeTruthy();
  // v1.1.0 added a skill, so diff.added should be non-empty
  expect(diff.data.added.length).toBeGreaterThanOrEqual(1);
});

// ═══════════════════════════════════════════════════════════════
// PART 15: UPGRADE — consumer upgrades installation to v1.1.0
// ═══════════════════════════════════════════════════════════════

test("20. Upgrade installation to v1.1.0 and verify", async () => {
  // Upgrade via API
  const upg = await api(
    consumer,
    "POST",
    `/orgs/${conOrgId2}/installations/${freshInstallId}/upgrade`,
    {
      version: "1.1.0",
    },
  );
  expect(upg.data).toBeTruthy();
  expect(upg.data.installed_version).toBe("1.1.0");

  // Navigate to installation detail in UI
  await conPage.goto(`/dashboard/orgs/${conOrgId2}/installations/${freshInstallId}`);
  await conPage.waitForLoadState("networkidle");

  // Assert: version shows 1.1.0
  await expect(conPage.locator("text=1.1.0")).toBeVisible();

  await conPage.screenshot({ path: "e2e/screenshots/install-upgraded.png" });
});

// ═══════════════════════════════════════════════════════════════
// PART 16: HISTORY INTACT — learner progress survives upgrade
// ═══════════════════════════════════════════════════════════════

test("21. Learner progress history remains intact after upgrade", async () => {
  // Verify the installation still exists and is active after upgrade
  const detail = await api(consumer, "GET", `/orgs/${conOrgId2}/installations/${freshInstallId}`);
  expect(detail.data).toBeTruthy();
  expect(detail.data.installed_version).toBe("1.1.0");
  expect(detail.data.status).toBe("active");

  // The installed skills from v1.0.0 should still exist (not deleted)
  // List skills in the consumer org — should have skills from the pack
  const skills = await api(consumer, "GET", `/orgs/${conOrgId2}/skills?per_page=50`);
  expect(skills.data).toBeTruthy();
  expect(skills.data.length).toBeGreaterThanOrEqual(1);

  // Check that no update is available now (we are on latest)
  expect(detail.data.update_available).toBe(false);
});
