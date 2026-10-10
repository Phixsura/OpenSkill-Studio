/**
 * Experiments console authorization wall — real-browser checks of the #59
 * posture for a NON-platform, non-delegated user (platform-admin flows are
 * covered by the live-API E2E, which can SQL-promote; the browser suite
 * deliberately tests the unprivileged side).
 */
import { test, expect } from "@playwright/test";
import { registerUser, loginInBrowser, type AuthContext } from "./helpers";

let student: AuthContext;

test.beforeAll(async () => {
  student = await registerUser("ExpWall Student");
});

test.describe("Experiments console wall (round 174)", () => {
  test("the sidebar shows no Experiments entry for a plain user", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await page.goto("/dashboard");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.locator("text=🌐 Ecosystem")).toBeVisible({ timeout: 30_000 });
    await expect(page.locator("text=🧪 Experiments")).toHaveCount(0);
  });

  test("a deep link to the console renders the error state, never a crash", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    await page.goto("/dashboard/experiments");
    await page.waitForLoadState("domcontentloaded");
    // the list query 403s; the page must stay alive and show no rows —
    // any client crash would blank the layout (sidebar gone)
    await expect(page.locator("text=Settings")).toBeVisible({ timeout: 30_000 });
    await expect(page.locator("table tbody tr")).toHaveCount(0);
  });

  // round 242: the deep-link posture holds on every console surface added
  // since round 174 — 403s render an alive error state, never a blank crash
  test("Explorer and Decisions deep links stay alive for a plain user", async ({ page }) => {
    await loginInBrowser(page, student.email, "TestPass123!");
    for (const path of ["/dashboard/experiments/metrics", "/dashboard/experiments/decisions"]) {
      await page.goto(path);
      await page.waitForLoadState("domcontentloaded");
      await expect(page.locator("text=Settings")).toBeVisible({
        timeout: 30_000,
      });
    }
  });
});
