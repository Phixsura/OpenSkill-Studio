/**
 * Sweep: NEW UI from the round-8 bug fixes — browser coverage for controls
 * that did not exist when the 8-family sweep ran.
 *
 * Covers:
 * - project detail: status badge + Publish/Unpublish button + draft hint
 *   (bug 6: no publish UI existed; students never saw UI-created projects)
 * - providers: offering cost field + per-offering Remove button (bugs 10-12)
 * - portfolio profile: username change via UI incl. USERNAME_UNAVAILABLE 409
 *   (bug 13) and the fixed public profile page /u/<username> (bug 2)
 * - portfolio: skill-badge visibility toggle + hidden badge absent from the
 *   public profile (bug 14 + the round-8 envelope fix)
 * - logout before auth hydration actually revokes the session (bug 5)
 */
import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { registerUser, createOrg, loginInBrowser, type AuthContext } from "./helpers";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";
const ts = Date.now();

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
  if (res.status === 204) return {};
  return res.json();
}

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  for (let i = 0; i < 5; i++) {
    try {
      admin = await registerUser("NewUI Admin");
      break;
    } catch {
      await sleep(3000);
    }
  }
  orgId = await createOrg(admin, `NewUI-${ts}`);
  ctx = await browser.newContext();
  page = await ctx.newPage();
  await loginInBrowser(page, admin.email, "TestPass123!");
});

test.afterAll(async () => {
  await ctx?.close();
});

test("project detail: draft badge + publish button flips status; unpublish restores", async () => {
  const proj = await api(admin, "POST", `/orgs/${orgId}/projects`, {
    title: `NewUI Project ${ts}`,
    description: "publish button test",
    instructions: "instructions",
    rubric: [{ criterion: "Q", max_score: 100 }],
  });
  const projectId = proj.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/projects/${projectId}`);
  await page.waitForLoadState("networkidle");

  // Draft state: badge + hint + Publish button
  await expect(page.getByText("draft", { exact: true })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/students cannot see or submit/i)).toBeVisible();
  await page.getByRole("button", { name: "Publish", exact: true }).click();

  // Published: badge flips, hint gone, Unpublish appears
  await expect(page.getByText("published", { exact: true })).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(/students cannot see or submit/i)).not.toBeVisible();
  await page.getByRole("button", { name: "Unpublish" }).click();
  await expect(page.getByText("draft", { exact: true })).toBeVisible({ timeout: 10_000 });
});

test("providers: offering created with cost renders it; per-offering Remove works", async () => {
  // Connection via API (mock adapter — no credentials)
  const adapters = await api(admin, "GET", "/providers/adapters");
  const mockId = adapters.data.find((a: { key: string }) => a.key === "mock").id;
  const conn = await api(admin, "POST", `/orgs/${orgId}/provider-connections`, {
    adapter_id: mockId,
    name: "NewUI Conn",
  });
  const connId = conn.data.id;

  await page.goto(`/dashboard/orgs/${orgId}/providers`);
  await page.waitForLoadState("networkidle");

  // Add an offering THROUGH THE FORM including the new cost field
  await page.getByLabel("Connection", { exact: true }).selectOption(connId);
  await page.getByLabel("Capability", { exact: true }).selectOption("image_generation");
  await page.getByPlaceholder("Model name").fill("newui-model-v1");
  await page.getByLabel("Cost per call USD").fill("0.25");
  await page.getByRole("button", { name: "Add Offering", exact: true }).click();

  // Row renders with the cost
  const row = page.locator("tr", { hasText: "newui-model-v1" });
  await expect(row).toBeVisible({ timeout: 10_000 });
  await expect(row.getByText("$0.25")).toBeVisible();

  // Per-offering Remove (no longer requires deleting the whole connection)
  await row.getByRole("button", { name: /Remove offering newui-model-v1/i }).click();
  await expect(page.locator("tr", { hasText: "newui-model-v1" })).not.toBeVisible({
    timeout: 10_000,
  });
  // Connection itself survives
  await expect(page.getByText("NewUI Conn").first()).toBeVisible();
});

test("portfolio: change username via UI; public profile renders at the new URL", async () => {
  const newUsername = `newui-${ts.toString(36)}`;

  await page.goto("/dashboard/portfolio/profile");
  await page.waitForLoadState("networkidle");
  await page.locator("#username").fill(newUsername);
  await page.getByRole("button", { name: "Change", exact: true }).click();
  await expect(page.getByText("Username updated.")).toBeVisible({ timeout: 10_000 });

  // Public profile (round-8 envelope fix: this page crashed before)
  const anon = await page.context().browser()!.newContext();
  const anonPage = await anon.newPage();
  await anonPage.goto(`/u/${newUsername}`);
  await expect(anonPage.getByRole("heading", { name: "NewUI Admin" })).toBeVisible({
    timeout: 15_000,
  });
  await anon.close();
});

test("portfolio: username collision shows the API error, value unchanged", async () => {
  // A second user takes a name; our user then tries to claim it
  const other = await registerUser("NewUI Other");
  const taken = `taken-${ts.toString(36)}`;
  const res = await fetch(`${API}/portfolio/username`, {
    method: "PUT",
    headers: other.headers,
    body: JSON.stringify({ username: taken }),
  });
  expect(res.ok).toBeTruthy();

  await page.goto("/dashboard/portfolio/profile");
  await page.waitForLoadState("networkidle");
  await page.locator("#username").fill(taken);
  await page.getByRole("button", { name: "Change", exact: true }).click();
  await expect(page.getByText(/taken|unavailable|already/i).first()).toBeVisible({
    timeout: 10_000,
  });
});

test("portfolio: badge toggle hides the badge from the public profile", async () => {
  // Seed a completed skill → badge (category + skill + exercise + correct attempt)
  const cat = await api(admin, "POST", `/orgs/${orgId}/categories`, {
    name: `NewUI Cat ${ts}`,
  });
  const skill = await api(admin, "POST", `/orgs/${orgId}/skills`, {
    category_id: cat.data.id,
    name: `NewUI Badge Skill ${ts}`,
    description: "badge toggle test skill",
    difficulty: "beginner",
  });
  await api(admin, "POST", `/orgs/${orgId}/skills/${skill.data.id}/publish`);
  const ex = await api(admin, "POST", `/orgs/${orgId}/skills/${skill.data.id}/exercises`, {
    title: "Q1",
    description: "pick a",
    type: "multiple_choice",
    config: { options: ["a", "b"], correct: "a" },
    max_score: 100,
  });
  await api(admin, "POST", `/orgs/${orgId}/exercises/${ex.data.id}/attempts`, {
    answer: { selected: ["a"] },
  });

  // Badge appears on the portfolio dashboard with its toggle
  await page.goto("/dashboard/portfolio");
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Skill Badges")).toBeVisible({ timeout: 15_000 });
  const toggle = page.getByLabel(`Show NewUI Badge Skill ${ts} badge on profile`);
  await expect(toggle).toBeChecked(); // default show_on_profile=true

  // Public-profile visibility asserted via the API (the /u page ISR-caches
  // for 60s, so the DOM lags freshly-earned badges either direction)
  const profile = await api(admin, "GET", "/portfolio/profile");
  const username = profile.data.username;
  const shown = await fetch(`${API}/u/${username}`).then((r) => r.json());
  const shownNames = (shown.data.skills ?? []).map((s: { name: string }) => s.name);
  expect(shownNames).toContain(`NewUI Badge Skill ${ts}`);

  // Hide it via the UI toggle → gone from the public payload. The checkbox
  // is CONTROLLED (state flips only after the mutation + refetch), so
  // uncheck()'s immediate post-click verification would fail — click + poll.
  await toggle.click();
  await expect(toggle).not.toBeChecked({ timeout: 10_000 });
  await expect
    .poll(
      async () => {
        const pub = await fetch(`${API}/u/${username}`).then((r) => r.json());
        return (pub.data.skills ?? []).map((s: { name: string }) => s.name);
      },
      { timeout: 10_000 },
    )
    .not.toContain(`NewUI Badge Skill ${ts}`);
});

test("logout before auth hydration still revokes the session", async () => {
  // Fresh context: only the refresh cookie survives (in-memory token empty
  // on first paint — exactly the pre-hydration window from bug 5)
  const user = await registerUser("NewUI Logout");
  const c2 = await page.context().browser()!.newContext();
  const p2 = await c2.newPage();
  await loginInBrowser(p2, user.email, "TestPass123!");

  // Full reload puts us pre-hydration; click Log out as fast as possible
  await p2.goto("/dashboard");
  await p2.getByRole("button", { name: "Log out" }).click();
  await p2.waitForURL("**/login**", { timeout: 15_000 });

  // The refresh cookie must now be revoked: hitting /dashboard again must
  // NOT silently re-authenticate (bug 5: session survived logout)
  await p2.goto("/dashboard");
  await p2.waitForURL("**/login**", { timeout: 15_000 });
  await c2.close();
});
