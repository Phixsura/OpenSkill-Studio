/**
 * Sweep: INTEGRATION FABRIC admin pages (issue #43, R323).
 *
 * Puts the five fabric pages into CI's Playwright job — until now the
 * sweep suite never visited them, so a route-group rename or a crashed
 * page component would ship invisibly (the deeper 63-check journey lives
 * in apps/api/tests/browser_e2e_integrations.mjs for local marathons;
 * this spec is the CI-fast render + one-action-per-page cut).
 *
 * DOM anchors read from the page sources, never guessed:
 * - hub: select aria-label "Provider", inputs "Connection name"/"Base URL"
 * - identity: input placeholder "school.example.edu", "Claim domain",
 *   token-name placeholder "Entra ID", mint button, "osks-verify-" TXT
 * - events: input aria-label "Webhook URL"/"Event patterns", "Subscribe",
 *   datalist #event-catalog-options, shown-once "Signing secret"
 * - sync: headings for mappings/profiles
 * - data: "Upload & preview", stream input aria-label "Stream name"
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

let admin: AuthContext;
let orgId: string;
let ctx: BrowserContext;
let page: Page;

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  admin = await registerUser("Fabric Sweep Admin");
  orgId = await createOrg(admin, `Fabric Sweep ${Date.now()}`);
  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, process.env.E2E_TEST_PASSWORD || "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

const intg = () => `/dashboard/orgs/${orgId}/integrations`;

test("hub renders catalog + health strip and creates a connection", async () => {
  await page.goto(intg());
  await expect(page.locator('select[aria-label="Provider"]')).toBeVisible();
  await page.selectOption('select[aria-label="Provider"]', "generic_rest");
  await page.fill('input[aria-label="Connection name"]', "CI Sweep ATS");
  await page.fill('input[aria-label="Base URL"]', "https://ats.example.com/api");
  await page.getByRole("button", { name: "Create", exact: true }).click();
  await expect(page.getByText("CI Sweep ATS")).toBeVisible({ timeout: 10000 });
});

test("identity claims a domain (TXT token shown) and mints a SCIM token once", async () => {
  await page.goto(`${intg()}/identity`);
  const domain = `ci-${Date.now()}.example.edu`;
  await page.fill('input[placeholder="school.example.edu"]', domain);
  await page.getByRole("button", { name: "Claim domain" }).click();
  await expect(page.getByText("osks-verify-").first()).toBeVisible({ timeout: 10000 });

  await page.fill('input[placeholder="Entra ID"]', "CI Sweep IdP");
  await page.getByRole("button", { name: /Mint/i }).click();
  await expect(page.getByText(/osks_scim_/).first()).toBeVisible({ timeout: 10000 });
  // shown-once: gone after reload
  await page.reload();
  await expect(page.getByText(/osks_scim_/)).toHaveCount(0);
});

test("events lists the catalog and creates a subscription with shown-once secret", async () => {
  await page.goto(`${intg()}/events`);
  await expect(page.locator("#event-catalog-options")).toBeAttached();
  await page.fill('input[aria-label="Webhook URL"]', "https://sink.example.com/ci-hook");
  await page.fill('input[aria-label="Event patterns"]', "com.openskill.project.approved.v1");
  await page.getByRole("button", { name: "Subscribe" }).click();
  await expect(page.getByText(/Signing secret \(shown once\)/)).toBeVisible({ timeout: 10000 });
  await expect(page.getByText("sink.example.com").first()).toBeVisible();
});

test("sync and data pages render; export stream created", async () => {
  await page.goto(`${intg()}/sync`);
  await expect(page.getByText(/mapping|profile/i).first()).toBeVisible();

  await page.goto(`${intg()}/data`);
  await expect(page.getByRole("button", { name: "Upload & preview" })).toBeVisible();
  const sname = `ci-${Date.now()}`;
  await page.fill('input[aria-label="Stream name"]', sname);
  await page.getByRole("button", { name: "Create stream" }).click();
  await expect(page.getByText(sname)).toBeVisible({ timeout: 10000 });
});
