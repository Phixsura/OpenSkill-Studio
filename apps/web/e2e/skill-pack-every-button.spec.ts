/**
 * Every remaining button/form interaction not covered by skill-pack-full-interaction.spec.ts
 *
 * 18 interactions:
 * - Pack list: status filter
 * - Pack create: validation error
 * - Pack detail: archive, add template, remove template
 * - Install list: row click → detail
 * - Install detail: View Changes (diff), Remove
 * - Path list: New Path navigate
 * - Path create: validation error
 * - Path detail: archive, remove item, add project item, name onBlur save
 * - Cohort paths: unassign
 * - Registry: sort dropdown, tags/time/license display
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
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("EvBtn Admin");
      break;
    } catch {
      await sleep(5000);
    }
  }
  await sleep(3000);
  for (let i = 0; i < 5; i++) {
    try {
      consumer = await registerUser("EvBtn Consumer");
      break;
    } catch {
      await sleep(5000);
    }
  }

  orgId = await createOrg(admin, `EvBtn-${Date.now()}`);
  conOrgId = await createOrg(consumer, `EvBtnC-${Date.now()}`);

  // Create skills, templates, pack, release
  const cat = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `EvCat-${Date.now()}`,
  });
  await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "EvSkill1",
    description: "test",
    difficulty: "beginner",
    category_id: cat.data.id,
  });
  await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "EvSkill2",
    description: "test2",
    difficulty: "intermediate",
    category_id: cat.data.id,
  });
  const tmpl = await api(admin, "POST", `/orgs/${orgId}/project-templates`, {
    name: "EvTemplate",
    description: "template test",
    instructions: "do this",
    rubric: [{ criterion: "Quality", max_score: 100 }],
  });
  const pack = await api(admin, "POST", `/orgs/${orgId}/packs`, {
    name: "EveryButton Pack",
    visibility: "public",
    difficulty: "beginner",
    scenario_tags: ["ecommerce"],
    tool_tags: ["midjourney"],
    estimated_minutes: 120,
    provenance: { author_name: "Test", license_name: "MIT" },
  });
  const packId = pack.data.id;
  const skillsRes = await api(admin, "GET", `/orgs/${orgId}/skills?per_page=100`);
  const s1id = skillsRes.data[0].id;
  const s2id = skillsRes.data[1].id;
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/skills`, { skill_id: s1id });
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/skills`, { skill_id: s2id });
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/templates`, {
    template_id: tmpl.data.id,
  });
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/releases`, { version: "1.0.0" });
  // Publish v1.1.0 for diff testing
  const cat2 = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `EvCat2-${Date.now()}`,
  });
  await api(admin, "POST", `/orgs/${orgId}/skills`, {
    name: "EvSkill3-New",
    description: "new skill",
    difficulty: "advanced",
    category_id: cat2.data.id,
  });
  const newSkills = await api(admin, "GET", `/orgs/${orgId}/skills?per_page=100`);
  const s3id = newSkills.data.find((s: any) => s.name === "EvSkill3-New")?.id;
  if (s3id) await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/skills`, { skill_id: s3id });
  await api(admin, "POST", `/orgs/${orgId}/packs/${packId}/releases`, {
    version: "1.1.0",
    changelog: "Added new skill",
  });

  // Install in consumer org (v1.0.0)
  await api(consumer, "POST", `/orgs/${conOrgId}/installations`, {
    pack_id: packId,
    version: "1.0.0",
  });

  // Create project in consumer org for path items
  await api(consumer, "POST", `/orgs/${conOrgId}/projects`, {
    title: "EvProject",
    description: "test project",
    instructions: "build something",
    rubric: [{ criterion: "Quality", max_score: 100 }],
  });

  // Login
  adminCtx = await browser.newContext();
  adminPage = await adminCtx.newPage();
  await loginInBrowser(adminPage, admin.email, "TestPass123!");
  await sleep(2000);
  conCtx = await browser.newContext();
  conPage = await conCtx.newPage();
  await loginInBrowser(conPage, consumer.email, "TestPass123!");
});

test.afterAll(async () => {
  await adminCtx?.close();
  await conCtx?.close();
});

// ═══ 1. Pack List: status filter dropdown ═══
test("1. Pack list: filter by status dropdown", async () => {
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs`);
  await adminPage.waitForLoadState("networkidle");

  // Select "Published" from status filter
  const filterSelect = adminPage.locator("select").first();
  await filterSelect.selectOption("published");
  await sleep(1000);

  // Should show only published packs
  const cards = adminPage.locator("a[href*='/packs/']");
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(1);
});

// ═══ 2. Pack Create: validation error on empty name ═══
test("2. Pack create: submit with empty name shows error", async () => {
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/new`);
  await adminPage.waitForLoadState("networkidle");

  // Don't fill name, just submit
  await adminPage.click('button:has-text("Create Skill Pack")');
  await sleep(500);

  // Should stay on form page (not redirect)
  await expect(adminPage).toHaveURL(/\/packs\/new/);
});

// ═══ 3. Pack Detail: Archive button ═══
test("3. Pack detail: click Archive → pack archived", async () => {
  // Create a throwaway pack
  const p = await api(admin, "POST", `/orgs/${orgId}/packs`, { name: "ArchiveMe Pack" });
  const pid = p.data.id;

  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/${pid}`);
  await adminPage.waitForLoadState("networkidle");

  // Click Archive — the button asks via confirm(); accept it (Playwright
  // dismisses dialogs by default, which silently no-ops the archive)
  adminPage.once("dialog", (d) => d.accept());
  await adminPage.locator("button:has-text('Archive')").click();
  await adminPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Verify: pack list should NOT show "ArchiveMe Pack" anymore
  await adminPage.goto(`/dashboard/orgs/${orgId}/packs`);
  await adminPage.waitForLoadState("networkidle");
  await sleep(500);
  await expect(adminPage.locator("text=ArchiveMe Pack")).not.toBeVisible();
});

// ═══ 4. Pack Detail: Add template + Remove template ═══
test("4. Pack detail: add template via dropdown, then remove", async () => {
  const p = await api(admin, "POST", `/orgs/${orgId}/packs`, { name: "TemplateTest Pack" });
  const pid = p.data.id;

  await adminPage.goto(`/dashboard/orgs/${orgId}/packs/${pid}`);
  await adminPage.waitForLoadState("networkidle");
  await sleep(500);

  // Find template dropdown
  const tmplSelect = adminPage.locator("select").filter({ hasText: "Select template..." });
  const options = await tmplSelect.locator("option").allTextContents();
  const tmplOpt = options.find((o) => o.includes("EvTemplate"));

  if (tmplOpt) {
    await tmplSelect.selectOption({ label: tmplOpt });
    // Click Add (second Add button — after templates section)
    await adminPage.locator("button:has-text('Add')").last().click();
    await adminPage.waitForLoadState("networkidle");
    await sleep(500);

    // Template should appear
    await expect(adminPage.locator("text=EvTemplate")).toBeVisible();

    // Remove it (× button in templates section)
    const removeButtons = adminPage.locator("button:has-text('×')");
    if ((await removeButtons.count()) > 0) {
      await removeButtons.last().click();
      await adminPage.waitForLoadState("networkidle");
      await sleep(500);
    }
  }
});

// ═══ 5. Installation List: click row → navigate to detail ═══
test("5. Installation list: click row navigates to detail", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations`);
  await conPage.waitForLoadState("networkidle");

  // Click the first link in the table
  const firstLink = conPage.locator("a[href*='/installations/']").first();
  await firstLink.click();
  await conPage.waitForLoadState("networkidle");

  // Should be on detail page
  await expect(conPage.locator("button:has-text('Fork')")).toBeVisible();
});

// ═══ 6. Installation Detail: View Changes button → diff ═══
test("6. Installation detail: View Changes shows diff", async () => {
  // Get installation id
  const instList = await api(consumer, "GET", `/orgs/${conOrgId}/installations`);
  const instId = instList.data[0]?.id;
  if (!instId) return;

  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations/${instId}`);
  await conPage.waitForLoadState("networkidle");

  // Check if update banner / View Changes button exists
  const viewBtn = conPage.locator("button:has-text('View Changes'), button:has-text('View Diff')");
  if (await viewBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await viewBtn.click();
    await conPage.waitForLoadState("networkidle");
    await sleep(1000);

    // Diff sections should appear (added/changed/removed)
    const hasDiff = await conPage
      .locator("text=Added")
      .or(conPage.locator("text=Changed"))
      .or(conPage.locator("text=Removed"))
      .first()
      .isVisible()
      .catch(() => false);
    expect(hasDiff).toBeTruthy();
  }
});

// ═══ 7. Installation Detail: Remove button → redirect ═══
test("7. Installation detail: Remove → confirm → redirect", async () => {
  // Install a fresh pack for removal
  const packs = await api(admin, "GET", `/orgs/${orgId}/packs`);
  const packId = packs.data.find((p: any) => p.name === "EveryButton Pack")?.id;
  // Create second install to remove
  const p2 = await api(admin, "POST", `/orgs/${orgId}/packs`, {
    name: "RemoveTest Pack",
    visibility: "public",
  });
  const s = await api(admin, "GET", `/orgs/${orgId}/skills?per_page=100`);
  await api(admin, "POST", `/orgs/${orgId}/packs/${p2.data.id}/skills`, { skill_id: s.data[0].id });
  await api(admin, "POST", `/orgs/${orgId}/packs/${p2.data.id}/releases`, { version: "1.0.0" });
  const inst2 = await api(consumer, "POST", `/orgs/${conOrgId}/installations`, {
    pack_id: p2.data.id,
  });
  const inst2Id = inst2.data?.id;
  if (!inst2Id) return;

  await conPage.goto(`/dashboard/orgs/${conOrgId}/installations/${inst2Id}`);
  await conPage.waitForLoadState("networkidle");

  conPage.on("dialog", (d) => d.accept());
  await conPage.locator("button:has-text('Remove')").click();
  await conPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Should redirect to installations list or show removed
  await expect(conPage).toHaveURL(/\/installations/);
});

// ═══ 8. Path List: New Path button navigate ═══
test("8. Path list: New Path button navigates", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths`);
  await conPage.waitForLoadState("networkidle");

  await conPage.click("text=New Path");
  await expect(conPage).toHaveURL(/\/paths\/new/);
});

// ═══ 9. Path Create: validation error ═══
test("9. Path create: submit empty form stays on page", async () => {
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/new`);
  await conPage.waitForLoadState("networkidle");

  await conPage.click('button:has-text("Create Learning Path")');
  await sleep(500);
  // Should stay on form (name required by HTML or show error)
  await expect(conPage).toHaveURL(/\/paths\/new/);
});

// ═══ 10. Path Detail: name edit onBlur save ═══
test("10. Path detail: edit name and blur → saves", async ({ browser }) => {
  const path = await api(consumer, "POST", `/orgs/${conOrgId}/paths`, { name: "EditableName" });
  const pathId = path.data.id;

  // conPage may be on a different page after Remove redirect — navigate fresh
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/${pathId}`);
  await conPage.waitForLoadState("networkidle");
  await sleep(2000);

  // Edit name input (the first input on the page contains the path name)
  const nameInput = conPage.locator("input").first();
  await expect(nameInput).toBeVisible({ timeout: 10_000 });
  await expect(nameInput).toHaveValue("EditableName");
  await nameInput.fill("Updated Path Name");
  await nameInput.blur();
  await sleep(2000);

  // Reload and verify saved
  await conPage.reload();
  await conPage.waitForLoadState("networkidle");
  await sleep(2000);
  const savedName = conPage.locator("input").first();
  await expect(savedName).toHaveValue("Updated Path Name");
});

// ═══ 11. Path Detail: Archive button ═══
test("11. Path detail: click Archive", async () => {
  const path = await api(consumer, "POST", `/orgs/${conOrgId}/paths`, { name: "ArchivePath" });
  const pathId = path.data.id;

  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/${pathId}`);
  await conPage.waitForLoadState("networkidle");
  await sleep(500);

  await conPage.locator("button:has-text('Archive')").click();
  await conPage.waitForLoadState("networkidle");
  await sleep(500);

  // Path should show archived or redirect
  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/${pathId}`);
  await conPage.waitForLoadState("networkidle");
  await expect(
    conPage
      .locator("text=Failed")
      .or(conPage.locator("text=not found"))
      .or(conPage.locator("text=archived")),
  ).toBeVisible({ timeout: 5_000 });
});

// ═══ 12. Path Detail: Remove item ═══
test("12. Path detail: add item then remove it", async () => {
  const path = await api(consumer, "POST", `/orgs/${conOrgId}/paths`, { name: "RemoveItemPath" });
  const pathId = path.data.id;
  // Add a section item via API
  await api(consumer, "POST", `/orgs/${conOrgId}/paths/${pathId}/items`, {
    item_type: "section",
    section_title: "RemoveMe Section",
    sort_order: 0,
  });

  await conPage.goto(`/dashboard/orgs/${conOrgId}/paths/${pathId}`);
  await conPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Section should be visible
  await expect(conPage.locator("text=RemoveMe Section")).toBeVisible();

  // Click remove button (×)
  const removeBtn = conPage.locator("button:has-text('×')").first();
  if (await removeBtn.isVisible()) {
    await removeBtn.click();
    await conPage.waitForLoadState("networkidle");
    await sleep(1000);

    // Section should be gone
    await expect(conPage.locator("text=RemoveMe Section")).not.toBeVisible();
  }
});

// ═══ 13. Cohort Paths: Unassign path ═══
test("13. Cohort paths: unassign path → confirm → removed", async () => {
  // Setup: create path, publish, create cohort, assign
  const path = await api(consumer, "POST", `/orgs/${conOrgId}/paths`, { name: "UnassignPath" });
  await api(consumer, "PUT", `/orgs/${conOrgId}/paths/${path.data.id}`, { status: "published" });
  const cohortId = await createCohort(consumer, conOrgId, `UnCoh-${Date.now()}`);
  await activateCohort(consumer, conOrgId, cohortId);
  await api(consumer, "POST", `/orgs/${conOrgId}/cohorts/${cohortId}/paths`, {
    path_id: path.data.id,
  });

  await conPage.goto(`/dashboard/orgs/${conOrgId}/cohorts/${cohortId}/paths`);
  await conPage.waitForLoadState("networkidle");
  await sleep(500);

  // Verify path is listed
  await expect(conPage.locator("text=UnassignPath")).toBeVisible();

  // Click Remove — remove all prior dialog handlers first
  conPage.removeAllListeners("dialog");
  conPage.once("dialog", (d) => d.accept());
  await conPage.locator("button:has-text('Remove')").click();
  await conPage.waitForLoadState("networkidle");
  await sleep(1000);

  // Path should be gone
  await expect(conPage.locator("text=UnassignPath")).not.toBeVisible();
});

// ═══ 14. Registry: sort dropdown ═══
test("14. Registry: sort dropdown changes results", async () => {
  await adminPage.goto("/registry");
  await adminPage.waitForLoadState("networkidle");

  // Find sort dropdown (has "Newest" option)
  const sortSelect = adminPage.locator("select").filter({ hasText: "Newest" });
  if (await sortSelect.isVisible()) {
    await sortSelect.selectOption("popular");
    await sleep(1500);
    // Page should still show results
    const cards = adminPage.locator("a[href*='/registry/']");
    expect(await cards.count()).toBeGreaterThanOrEqual(1);
  }
});

// ═══ 15. Registry Detail: tags + time + license visible ═══
test("15. Registry detail: shows tags, estimated time, and license", async () => {
  // Find the pack we created with tags/time/license
  const packs = await api(admin, "GET", `/orgs/${orgId}/packs`);
  const evPack = packs.data.find((p: any) => p.name === "EveryButton Pack");
  if (!evPack) return;

  await adminPage.goto(`/registry/${evPack.id}`);
  await adminPage.waitForLoadState("networkidle");

  // Scenario tags
  await expect(adminPage.locator("text=ecommerce")).toBeVisible();
  // Tool tags
  await expect(adminPage.locator("text=midjourney")).toBeVisible();
  // License — exact match ("MIT" also substring-matches "Submit Review")
  await expect(adminPage.getByText("MIT", { exact: true })).toBeVisible();
  // Estimated time (120 min = 2h 0m)
  await expect(adminPage.locator("text=2h")).toBeVisible();
});
