/**
 * Sweep: AUTH + ONBOARDING + SETTINGS browser E2E.
 *
 * Pages exercised: /login, /register, /forgot-password, /dashboard,
 * /dashboard/settings, /dashboard/orgs, /dashboard/orgs/new, /join/[code].
 *
 * DOM anchors (verified against page sources):
 * - Login:    #email, #password, button "Log in", error div[role=alert]
 * - Register: #displayName, #email, #password, button "Sign up", div[role=alert]
 * - Forgot:   #email, button "Send reset link", "Check your email" heading
 * - Settings: #email (disabled), #displayName, button "Save changes",
 *             "Profile updated." message
 * - Orgs new: #name, #slug, #description, button "Create Organization"
 * - Orgs list: "Create Organization" button, empty state
 *             "You don't belong to any organizations yet."
 * - Sidebar:  button "Log out"
 * - Join:     button "Accept & Join", success text "You've joined the
 *             organization", logged-out prompt "You need to log in..."
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
const PASSWORD = "TestPass123!";

let admin: AuthContext; // API-seeded owner of the invite org
let adminOrgId: string;
let inviteCode: string;
let ctx: BrowserContext;
let page: Page;

// The user we register through the browser UI
const uiName = "Sweep Auth User";
const uiEmail = `sweep-auth-${Date.now()}@test.com`;
const orgName = `SweepAuth Org ${Date.now()}`;
const orgSlug = `sweep-auth-org-${Date.now()}`;

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

/** The visible error alert (excludes Next.js's empty route announcer,
 * which also carries role="alert"). */
function errorAlert(p: Page) {
  return p.getByRole("alert").filter({ hasText: /\S/ }).first();
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  // Seed an admin + org + invite link entirely via API (no browser needed)
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("Sweep Auth Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  adminOrgId = await createOrg(admin, `SweepAuthInvite-${Date.now()}`);

  const linkRes = await fetch(`${API}/orgs/${adminOrgId}/invite-links`, {
    method: "POST",
    headers: admin.headers,
    body: JSON.stringify({ role: "student" }),
  });
  const linkData = await linkRes.json();
  inviteCode = linkData.data.code;

  ctx = await browser.newContext();
  page = await ctx.newPage();
});

test.afterAll(async () => {
  await ctx?.close();
});

// ── Phase 1: logged-out flows ────────────────────────────────

test("protected route redirect: /dashboard/settings logged-out → /login", async () => {
  await page.goto("/dashboard/settings");
  await page.waitForURL(/\/login\?redirect=/, { timeout: 15_000 });
  expect(page.url()).toContain("redirect=%2Fdashboard%2Fsettings");
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
});

test("join page logged-out: prompts to log in or sign up", async () => {
  await page.goto(`/join/${inviteCode}`);
  // Page waits up to 2s for auth hydration before showing the prompt
  await expect(page.getByText("You need to log in or create an account first.")).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByRole("button", { name: "Log in" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign up" })).toBeVisible();
});

test("forgot password: submitting email shows confirmation", async () => {
  await page.goto("/forgot-password");
  await expect(page.getByRole("heading", { name: "Reset password" })).toBeVisible();
  await page.locator("#email").fill("whoever@example.com");
  await page.getByRole("button", { name: "Send reset link" }).click();
  await expect(page.getByRole("heading", { name: "Check your email" })).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByText(/If an account exists for/)).toBeVisible();
});

test("register: weak password shows validation error in UI", async () => {
  await page.goto("/register");
  await page.locator("#displayName").fill(uiName);
  await page.locator("#email").fill(uiEmail);
  // 8+ chars but no uppercase → client-side rule fires
  await page.locator("#password").fill("weakpass1");
  await page.getByRole("button", { name: "Sign up" }).click();
  await expect(errorAlert(page)).toContainText(
    "Password must contain at least one uppercase letter.",
  );
  // Still on /register — nothing submitted
  expect(page.url()).toContain("/register");

  // Too short → the length rule fires
  await page.locator("#password").fill("Ab1");
  await page.getByRole("button", { name: "Sign up" }).click();
  await expect(errorAlert(page)).toContainText("Password must be at least 8 characters.");
});

test("register: duplicate email shows server error in UI", async () => {
  await page.goto("/register");
  await page.locator("#displayName").fill("Dup Email User");
  await page.locator("#email").fill(admin.email); // already registered in beforeAll
  await page.locator("#password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign up" }).click();
  await expect(errorAlert(page)).toContainText("An account with this email already exists", {
    timeout: 10_000,
  });
});

test("register: happy path via UI form → dashboard", async () => {
  await page.goto("/register");
  await page.locator("#displayName").fill(uiName);
  await page.locator("#email").fill(uiEmail);
  await page.locator("#password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign up" }).click();

  // The success screen ("Check your email") may auto-redirect immediately:
  // the isAuthenticated effect fires router.replace("/dashboard") as soon
  // as registration sets auth. Accept either path.
  await Promise.race([
    page.waitForURL("**/dashboard", { timeout: 15_000 }),
    page.getByRole("button", { name: "Continue to Dashboard" }).waitFor({ timeout: 15_000 }),
  ]);
  if (!page.url().includes("/dashboard")) {
    await page.getByRole("button", { name: "Continue to Dashboard" }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });
  }
  await expect(page.getByRole("heading", { name: `Welcome, ${uiName}` })).toBeVisible({
    timeout: 15_000,
  });
});

// ── Phase 2: logged-in as the UI-registered user ─────────────

test("orgs list: empty state for a brand-new user", async () => {
  await page.goto("/dashboard/orgs");
  await expect(page.getByRole("heading", { name: "Organizations" })).toBeVisible();
  await expect(page.getByText(/don't belong to any organizations yet/)).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByRole("button", { name: "Create your first organization" })).toBeVisible();
});

test("create org via UI form → lands on org detail page", async () => {
  await page.goto("/dashboard/orgs/new");
  await expect(page.getByRole("heading", { name: "Create Organization" })).toBeVisible();
  await page.locator("#name").fill(orgName);
  await page.locator("#slug").fill(orgSlug);
  await page.locator("#description").fill("E2E sweep-auth org");
  await page.getByRole("button", { name: "Create Organization" }).click();

  await page.waitForURL(/\/dashboard\/orgs\/[0-9A-Z]{26}$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: orgName })).toBeVisible({
    timeout: 15_000,
  });
  // Owner role card visible on the overview
  await expect(page.getByText("Your role")).toBeVisible();
});

test("create org: duplicate slug shows server error in UI", async () => {
  await page.goto("/dashboard/orgs/new");
  await page.locator("#name").fill(`${orgName} Twin`);
  await page.locator("#slug").fill(orgSlug); // same slug as previous test
  await page.getByRole("button", { name: "Create Organization" }).click();
  await expect(page.getByText("An organization with this slug already exists")).toBeVisible({
    timeout: 10_000,
  });
  // Still on the create form
  expect(page.url()).toContain("/dashboard/orgs/new");
});

test("orgs list: created org appears", async () => {
  await page.goto("/dashboard/orgs");
  await expect(page.getByRole("heading", { name: orgName, exact: true })).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByText("owner").first()).toBeVisible();
});

test("settings: renders user info; display-name change persists after reload", async () => {
  await page.goto("/dashboard/settings");
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();

  // Email shown (disabled input)
  await expect(page.locator("#email")).toHaveValue(uiEmail, { timeout: 15_000 });
  await expect(page.locator("#email")).toBeDisabled();
  await expect(page.locator("#displayName")).toHaveValue(uiName, { timeout: 15_000 });

  const newName = "Sweep Auth Renamed";
  await page.locator("#displayName").fill(newName);
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(page.getByText("Profile updated.")).toBeVisible({ timeout: 10_000 });

  // Sidebar reflects the new name immediately
  await expect(page.getByText(newName).first()).toBeVisible();

  // Persists across a full reload (session restored via refresh cookie)
  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.locator("#displayName")).toHaveValue(newName, { timeout: 15_000 });
  await expect(page.locator("#email")).toHaveValue(uiEmail);
});

// ── Phase 3: org invite join ─────────────────────────────────

test("join via invite link: accept creates membership + success message", async () => {
  await page.goto(`/join/${inviteCode}`);
  await expect(page.getByRole("button", { name: "Accept & Join" })).toBeVisible({
    timeout: 15_000,
  });
  await page.getByRole("button", { name: "Accept & Join" }).click();
  await expect(page.getByText("You've joined the organization. Redirecting...")).toBeVisible({
    timeout: 10_000,
  });

  // Verify membership actually exists (API, as org owner)
  const res = await fetch(`${API}/orgs/${adminOrgId}/members`, {
    headers: admin.headers,
  });
  const members = await res.json();
  const emails = (members.data ?? []).map(
    (m: { user?: { email?: string }; email?: string }) => m.user?.email ?? m.email,
  );
  expect(emails).toContain(uiEmail);
});

// APP BUG: join success redirect goes to /dashboard/orgs/undefined.
// The API returns { data: { org_id, message } } (DataResponse envelope) but
// src/app/join/[code]/page.tsx line ~77 types the response as { org_id } and
// reads res.org_id — undefined. Fix: read res.data.org_id.
test("join redirect lands on the joined org page", async () => {
  // After the success message the page router.push()es to the org.
  // Continues from previous test's page state (success screen).
  await page.waitForURL(/\/dashboard\/orgs\/.+/, { timeout: 15_000 });
  expect(page.url()).toContain(`/dashboard/orgs/${adminOrgId}`);
});

test("join with invalid code: error shown in UI", async () => {
  await page.goto("/join/totally-bogus-code-123");
  await expect(page.getByRole("button", { name: "Accept & Join" })).toBeVisible({
    timeout: 15_000,
  });
  await page.getByRole("button", { name: "Accept & Join" }).click();
  await expect(page.getByText("Invite link not found or inactive")).toBeVisible({
    timeout: 10_000,
  });
});

// ── Phase 4: logout + login ──────────────────────────────────

test("logout via UI → redirected to login; dashboard protected again", async () => {
  await page.goto("/dashboard");
  // APP BUG (race): clicking "Log out" before the AuthInitializer session
  // refresh completes sends the logout request with no Bearer token; the API
  // logout endpoint requires get_current_user, so it 401s silently and the
  // refresh cookie is never revoked/cleared — the UI redirects to /login but
  // the next /dashboard visit silently re-authenticates. Wait for the
  // authenticated sidebar (user email rendered) so logout carries a token.
  await expect(page.getByText(uiEmail)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("button", { name: "Log out" })).toBeVisible({
    timeout: 15_000,
  });
  await page.getByRole("button", { name: "Log out" }).click();
  await page.waitForURL(/\/login/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();

  // Refresh cookie was cleared — middleware bounces /dashboard back to /login
  await page.goto("/dashboard");
  await page.waitForURL(/\/login/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
});

test("login: wrong password shows error in UI", async () => {
  await page.goto("/login");
  await page.locator("#email").fill(uiEmail);
  await page.locator("#password").fill("WrongPass999!");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(errorAlert(page)).toContainText("Invalid email or password", {
    timeout: 10_000,
  });
  // Still on login page
  expect(page.url()).toContain("/login");
});

test("login: success → dashboard shows welcome", async () => {
  await loginInBrowser(page, uiEmail, PASSWORD);
  await expect(page.getByRole("heading", { name: /Welcome, Sweep Auth Renamed/ })).toBeVisible({
    timeout: 15_000,
  });
});
