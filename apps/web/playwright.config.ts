import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for OpenSkill Studio browser E2E tests.
 *
 * Requires both backend (port 8000) and frontend (port 3000) running.
 * Start with: make dev-api & make dev-web
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false, // sequential — tests share DB state
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "html",
  timeout: 60_000,
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // Don't auto-start webServer — user starts manually or CI script handles it
});
