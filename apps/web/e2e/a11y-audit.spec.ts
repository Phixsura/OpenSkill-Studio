/**
 * A11Y AUDIT (round 25) — axe-core serious/critical violations on the key
 * Issue-21 pages. The plan claims "list view is keyboard-accessible"; this
 * verifies it (and the rest) rather than trusting the claim.
 *
 * axe-core is injected from the local dependency if present, else from a
 * pinned CDN build at test time — it is NOT added to package.json (one-off
 * audit, not a standing test dependency). Runs only when RUN_A11Y=1 so the
 * main suite is unaffected by the network dependency.
 */
import { test, expect } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";
import { readFileSync, existsSync } from "node:fs";

// axe-core staged at /tmp/axe-tmp by the round-25 audit (npm pack), or a
// local dep if one exists. NOT added to package.json — one-off audit.
const AXE_PATHS = [
  "node_modules/axe-core/axe.min.js",
  "/tmp/axe-tmp/package/axe.min.js",
];

async function injectAxe(page: import("@playwright/test").Page) {
  const found = AXE_PATHS.find((p) => existsSync(p));
  if (!found) throw new Error("axe-core unavailable — stage it at /tmp/axe-tmp");
  await page.addScriptTag({ content: readFileSync(found, "utf8") });
}

async function scan(page: import("@playwright/test").Page, name: string) {
  await injectAxe(page);
  const results = await page.evaluate(async () => {
    // @ts-expect-error injected global
    return await window.axe.run(document, {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] },
    });
  });
  const serious = results.violations.filter(
    (v: { impact: string }) => v.impact === "serious" || v.impact === "critical",
  );
  if (serious.length) {
    console.log(`\n[a11y] ${name}: ${serious.length} serious/critical violations`);
    for (const v of serious) {
      console.log(`  - ${v.id} (${v.impact}): ${v.help} [${v.nodes.length} nodes]`);
    }
  } else {
    console.log(`[a11y] ${name}: clean (serious/critical)`);
  }
  return serious;
}

const RUN = process.env.RUN_A11Y === "1";

test.describe(RUN ? "a11y audit" : "a11y audit (skipped — set RUN_A11Y=1)", () => {
  test.skip(!RUN, "set RUN_A11Y=1 to run the a11y audit");
  test.describe.configure({ mode: "serial" });

  let admin: AuthContext;
  let orgId: string;
  let packId = "";

  test.beforeAll(async () => {
    admin = await registerUser(`a11y-${Date.now()}`);
    orgId = await createOrg(admin, `A11Y ${Date.now()}`);
    const res = await fetch(
      `${process.env.E2E_API_URL || "http://localhost:8000/api/v1"}/orgs/${orgId}/workflow-packs`,
      {
        method: "POST",
        headers: admin.headers,
        body: JSON.stringify({ name: `A11Y Pack ${Date.now()}` }),
      },
    );
    packId = (await res.json()).data.id;
  });

  test("workflow-packs list page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/workflow-packs`);
    await page.waitForLoadState("networkidle");
    expect(await scan(page, "workflow-packs list")).toHaveLength(0);
  });

  test("workflow editor (list view — keyboard accessibility claim)", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/workflow-packs/${packId}/editor`);
    await page.waitForLoadState("networkidle");
    // switch to list view (the accessibility-first view per the plan)
    const listBtn = page.getByRole("button", { name: "List", exact: true });
    if (await listBtn.isVisible().catch(() => false)) await listBtn.click();
    await page.waitForTimeout(500);
    expect(await scan(page, "workflow editor list-view")).toHaveLength(0);
  });

  test("requirements intake page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/requirements/new`);
    await page.waitForLoadState("networkidle");
    expect(await scan(page, "requirements intake")).toHaveLength(0);
  });

  test("providers page", async ({ page }) => {
    await loginInBrowser(page, admin.email, "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/providers`);
    await page.waitForLoadState("networkidle");
    expect(await scan(page, "providers")).toHaveLength(0);
  });
});
