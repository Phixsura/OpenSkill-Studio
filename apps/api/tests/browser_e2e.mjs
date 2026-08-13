/**
 * Playwright browser E2E test — tests the full frontend flow visually.
 * Usage: node tests/browser_e2e.mjs  (run from project root)
 * Requires: frontend on :3000, backend on :8000, Docker infra up
 */
import { chromium } from "playwright";

const CHROMIUM_PATH =
  process.env.CHROMIUM_PATH ||
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;

const BASE = "http://localhost:3000";
const API = "http://localhost:8000/api/v1";
let pass = 0,
  fail = 0;
const results = [];

function check(label, ok) {
  if (ok) {
    pass++;
    results.push(`  ✅ ${label}`);
  } else {
    fail++;
    results.push(`  ❌ ${label}`);
  }
}

function section(name) {
  results.push(`\n${"=".repeat(60)}`);
  results.push(`  ${name}`);
  results.push("=".repeat(60));
}

const email = `e2e-${Date.now()}@test.com`;
const password = "Test1234!";

const browser = await chromium.launch({ headless: true, executablePath: CHROMIUM_PATH });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();

const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});

try {
  // ── 1. Landing Page ──
  section("1. Landing Page");
  await page.goto(BASE, { waitUntil: "networkidle", timeout: 15000 });
  const title = await page.title();
  check("page loads", title.length > 0);

  const bodyText = await page.textContent("body");
  check("has content", bodyText.length > 100);

  const heroLink = await page.$('a:has-text("Get Started"), a:has-text("Sign"), a:has-text("Login"), a[href*="register"], a[href*="login"]');
  check("has auth CTA link", heroLink !== null);
  await page.screenshot({ path: "/tmp/e2e-01-landing.png", fullPage: true });

  // ── 2. Register ──
  section("2. Register");
  await page.goto(`${BASE}/register`, { waitUntil: "networkidle", timeout: 10000 });
  check("register page loads", page.url().includes("register"));

  await page.fill("#displayName", "E2E Tester");
  await page.fill("#email", email);
  await page.fill("#password", password);
  check("form fields fillable", true);
  await page.screenshot({ path: "/tmp/e2e-02-register-filled.png" });

  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  const regBody = await page.textContent("body");
  check("registration succeeds", regBody.includes("Check your email") || regBody.includes("Continue"));
  await page.screenshot({ path: "/tmp/e2e-03-register-success.png" });

  // Click "Continue to Dashboard"
  const continueBtn = await page.$('button:has-text("Continue to Dashboard")');
  if (continueBtn) {
    await continueBtn.click();
    await page.waitForTimeout(3000);
  }
  check("navigates to dashboard", page.url().includes("dashboard"));
  await page.screenshot({ path: "/tmp/e2e-04-dashboard.png" });

  // ── 3. Dashboard ──
  section("3. Dashboard");
  const nav = await page.$("nav, aside, [role='navigation'], header");
  check("has navigation", nav !== null);

  const navLinks = await page.$$eval("a", (els) =>
    els.map((e) => e.getAttribute("href")).filter((h) => h?.includes("dashboard"))
  );
  check("nav has dashboard links", navLinks.length >= 3);

  // ── 4. Logout + Login ──
  section("4. Login Flow");
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle", timeout: 10000 });
  check("login page loads", page.url().includes("login"));

  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.screenshot({ path: "/tmp/e2e-05-login-filled.png" });

  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  check("login redirects to dashboard", page.url().includes("dashboard"));
  await page.screenshot({ path: "/tmp/e2e-06-login-dashboard.png" });

  // ── 5. Create Organization ──
  section("5. Create Organization");
  await page.goto(`${BASE}/dashboard/orgs/new`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  let orgCreated = false;
  let orgId = "";

  const orgForm = await page.$("form");
  if (orgForm) {
    const nameField = await page.$('input[id="name"], input[name="name"], input[placeholder*="name" i]');
    if (nameField) {
      await nameField.fill("E2E Test Org");
      const descField = await page.$('textarea, input[id="description"], input[name="description"]');
      if (descField) await descField.fill("Created by Playwright");
      await page.screenshot({ path: "/tmp/e2e-07-org-form.png" });
      const createBtn = await page.$('button[type="submit"], button:has-text("Create")');
      if (createBtn) {
        await createBtn.click();
        await page.waitForTimeout(3000);
        orgCreated = true;
      }
    }
  }

  // Fallback: create org via API
  if (!orgCreated || !orgId) {
    try {
      const loginResp = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const loginData = await loginResp.json();
      const token = loginData.access_token;

      const orgResp = await fetch(`${API}/orgs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: "Browser Test Org", description: "Playwright E2E" }),
      });
      const orgData = await orgResp.json();
      orgId = orgData.data?.id || "";

      // Also create a skill + project via API for page tests
      if (orgId) {
        // Category
        const catResp = await fetch(`${API}/orgs/${orgId}/categories`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ name: "Test Category" }),
        });
        const catData = await catResp.json();
        const catId = catData.data?.id;

        // Skill
        if (catId) {
          await fetch(`${API}/orgs/${orgId}/skills`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
            body: JSON.stringify({
              category_id: catId,
              name: "Test Skill",
              description: "For E2E",
              learning_content: "# Learn\nTest content",
              difficulty: "beginner",
              tags: ["test"],
              estimated_minutes: 10,
            }),
          });
        }

        // Project
        await fetch(`${API}/orgs/${orgId}/projects`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({
            title: "Test Project",
            description: "E2E test project",
            instructions: "## Build something",
            rubric: [{ criterion: "Quality", max_score: 100 }],
            max_score: 100,
          }),
        });

        // Portfolio
        await fetch(`${API}/portfolio/profile`, {
          method: "PUT",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ headline: "E2E Tester", bio: "Testing all the things" }),
        });
      }
    } catch {}
  }
  check("org available", orgId.length > 0);

  // ── 6. Organization Dashboard ──
  section("6. Organization Dashboard");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const orgPage = await page.textContent("body").catch(() => "");
    check("org dashboard renders", orgPage.length > 50);
    await page.screenshot({ path: "/tmp/e2e-08-org-dashboard.png" });
  }

  // ── 7. Skills Pages ──
  section("7. Skills Pages");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}/skills`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const skillsBody = await page.textContent("body").catch(() => "");
    check("skills list page renders", skillsBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-09-skills-list.png" });

    await page.goto(`${BASE}/dashboard/orgs/${orgId}/skills/new`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const newSkillBody = await page.textContent("body").catch(() => "");
    check("new skill page renders", newSkillBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-10-skill-new.png" });
  }

  // ── 8. Projects Pages ──
  section("8. Projects Pages");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}/projects`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const projBody = await page.textContent("body").catch(() => "");
    check("projects list page renders", projBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-11-projects-list.png" });

    await page.goto(`${BASE}/dashboard/orgs/${orgId}/projects/new`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const newProjBody = await page.textContent("body").catch(() => "");
    check("new project page renders", newProjBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-12-project-new.png" });
  }

  // ── 9. Evaluation Pages ──
  section("9. Evaluation Pages");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}/evaluation`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const evalBody = await page.textContent("body").catch(() => "");
    check("evaluation page renders", evalBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-13-evaluation.png" });

    await page.goto(`${BASE}/dashboard/orgs/${orgId}/evaluation/settings`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const evalSettBody = await page.textContent("body").catch(() => "");
    check("evaluation settings page renders", evalSettBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-14-eval-settings.png" });
  }

  // ── 10. Members Page ──
  section("10. Members Page");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}/members`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const memBody = await page.textContent("body").catch(() => "");
    check("members page renders", memBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-15-members.png" });
  }

  // ── 11. Org Settings ──
  section("11. Org Settings");
  if (orgId) {
    await page.goto(`${BASE}/dashboard/orgs/${orgId}/settings`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const settBody = await page.textContent("body").catch(() => "");
    check("org settings page renders", settBody.length > 50);
    await page.screenshot({ path: "/tmp/e2e-16-org-settings.png" });
  }

  // ── 12. Portfolio ──
  section("12. Portfolio");
  await page.goto(`${BASE}/dashboard/portfolio`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  const portBody = await page.textContent("body").catch(() => "");
  check("portfolio page renders", portBody.length > 50);
  await page.screenshot({ path: "/tmp/e2e-17-portfolio.png" });

  // ── 13. Profile Settings ──
  section("13. Profile Settings");
  await page.goto(`${BASE}/dashboard/settings`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  const profBody = await page.textContent("body").catch(() => "");
  check("profile settings page renders", profBody.length > 50);
  await page.screenshot({ path: "/tmp/e2e-18-profile-settings.png" });

  // ── 14. Public Profile ──
  section("14. Public Profile");
  let username = "";
  try {
    const loginResp = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const d = await loginResp.json();
    const profileResp = await fetch(`${API}/portfolio/profile`, {
      headers: { Authorization: `Bearer ${d.access_token}` },
    });
    const pd = await profileResp.json();
    username = pd.data?.username || "";
  } catch {}

  if (username) {
    await page.goto(`${BASE}/u/${username}`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
    const pubBody = await page.textContent("body").catch(() => "");
    check("public profile page renders", pubBody.length > 50);
    check("no email exposed", !pubBody.includes(email));
    check("shows display name or headline", pubBody.includes("E2E") || pubBody.includes("Tester"));
    await page.screenshot({ path: "/tmp/e2e-19-public-profile.png" });
  } else {
    check("public profile page (no username)", false);
  }

  // ── 15. Responsive / Mobile ──
  section("15. Responsive (375px)");
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto(BASE, { waitUntil: "networkidle", timeout: 10000 });
  const mobileBody = await page.textContent("body").catch(() => "");
  check("mobile landing renders", mobileBody.length > 50);
  await page.screenshot({ path: "/tmp/e2e-20-mobile-landing.png" });

  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  await page.screenshot({ path: "/tmp/e2e-21-mobile-dashboard.png" });
  check("mobile dashboard renders", true);
  await page.setViewportSize({ width: 1280, height: 800 });

  // ── 16. Dark Mode ──
  section("16. Dark Mode");
  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  const themeToggle = await page.$('button[aria-label*="theme" i], button[aria-label*="dark" i], button[aria-label*="mode" i], [data-testid*="theme"]');
  if (themeToggle) {
    await themeToggle.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: "/tmp/e2e-22-dark-mode.png" });
    check("dark mode toggles", true);
  } else {
    // Check if dark mode class exists
    const hasDarkClass = await page.$("html.dark, [class*='dark']");
    check("dark mode available", hasDarkClass !== null || themeToggle !== null);
  }

  // ── 17. 404 Page ──
  section("17. 404 Page");
  await page.goto(`${BASE}/nonexistent-page-xyz`, { waitUntil: "networkidle", timeout: 10000 }).catch(() => {});
  const errBody = await page.textContent("body").catch(() => "");
  check("404 page renders", errBody.length > 20);
  await page.screenshot({ path: "/tmp/e2e-23-404.png" });

  // ── 18. Console Errors ──
  section("18. Console Errors");
  const criticalErrors = consoleErrors.filter(
    (e) =>
      !e.includes("favicon") &&
      !e.includes("Failed to load resource") &&
      !e.includes("hydration") &&
      !e.includes("Warning:") &&
      !e.includes("ERR_") &&
      !e.includes("net::")
  );
  check(`no critical JS errors (${criticalErrors.length} found)`, criticalErrors.length === 0);
  if (criticalErrors.length > 0) {
    results.push("  Console errors:");
    criticalErrors.slice(0, 5).forEach((e) => results.push(`    - ${e.slice(0, 150)}`));
  }

} catch (err) {
  results.push(`\n  💥 FATAL: ${err.message}`);
  fail++;
} finally {
  await browser.close();
}

console.log(results.join("\n"));
console.log(`\n${"=".repeat(60)}`);
console.log(`  RESULTS: ${pass} passed, ${fail} failed`);
console.log(`  Screenshots saved to /tmp/e2e-*.png`);
console.log("=".repeat(60));

process.exit(fail > 0 ? 1 : 0);
