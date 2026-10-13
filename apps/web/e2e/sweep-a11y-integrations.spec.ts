/**
 * A11Y sweep: INTEGRATION FABRIC pages (issue #43, R383).
 *
 * axe-core WCAG 2.1 A/AA over the five fabric pages as an authenticated
 * org admin, failing CI on any serious/critical violation. Unlike the
 * RUN_A11Y-gated one-off audit (a11y-audit.spec.ts), this runs
 * unconditionally: axe-core is a real workspace devDependency (R372), so
 * there is no network fetch and no staging step.
 */
import { readFileSync } from "node:fs";
import { test, expect, type Page } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const AXE_SRC = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

let admin: AuthContext;
let orgId: string;

test.describe.configure({ mode: "serial" });

test.beforeAll(async () => {
  admin = await registerUser("Fabric A11y Admin");
  orgId = await createOrg(admin, `Fabric A11y Org ${Date.now()}`);
});

async function scan(page: Page, name: string) {
  await page.addScriptTag({ content: AXE_SRC });
  const results = await page.evaluate(async () => {
    // @ts-expect-error injected global
    return await window.axe.run(document, {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
      resultTypes: ["violations"],
    });
  });
  const serious = results.violations.filter(
    (v: { impact: string }) => v.impact === "serious" || v.impact === "critical",
  );
  if (serious.length) {
    console.log(
      `[a11y] ${name}:`,
      serious
        .map(
          (v: { id: string; impact: string; nodes: unknown[] }) =>
            `${v.id}(${v.impact})x${v.nodes.length}`,
        )
        .join(", "),
    );
  }
  expect(serious, `${name} has serious/critical a11y violations`).toHaveLength(0);
}

const PAGES = ["", "/identity", "/events", "/sync", "/data"] as const;

for (const suffix of PAGES) {
  const label = suffix || "/hub";
  test(`fabric ${label} page passes WCAG 2.1 A/AA (serious/critical)`, async ({ page }) => {
    await loginInBrowser(page, admin.email, process.env.E2E_TEST_PASSWORD || "TestPass123!");
    await page.goto(`/dashboard/orgs/${orgId}/integrations${suffix}`);
    await page.waitForLoadState("load");
    await page.waitForTimeout(1500); // client data settle
    await scan(page, `integrations${label}`);
  });
}
