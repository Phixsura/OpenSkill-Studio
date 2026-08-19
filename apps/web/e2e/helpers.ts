/**
 * Shared helpers for E2E browser tests.
 *
 * Uses the API directly (not browser UI) for setup steps that would be
 * tedious to click through, so the browser test can focus on verifying
 * the UI renders and responds correctly.
 */

import { type Page } from "@playwright/test";

const API = process.env.E2E_API_URL || "http://localhost:8000/api/v1";

let counter = 0;

function uniqueEmail(): string {
  counter++;
  return `e2e-${Date.now()}-${counter}@test.com`;
}

export interface AuthContext {
  token: string;
  userId: string;
  email: string;
  headers: Record<string, string>;
}

/** Register a user via API, return auth context. */
export async function registerUser(name: string): Promise<AuthContext> {
  const email = uniqueEmail();
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password: "TestPass123!", display_name: name }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`registerUser failed (${res.status}): ${text}`);
  }
  const data = await res.json();
  return {
    token: data.access_token,
    userId: data.user.id,
    email,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${data.access_token}`,
    },
  };
}

/** Create an org via API. */
export async function createOrg(auth: AuthContext, name: string): Promise<string> {
  const res = await fetch(`${API}/orgs`, {
    method: "POST",
    headers: auth.headers,
    body: JSON.stringify({ name }),
  });
  const data = await res.json();
  return data.data.id;
}

/** Add a member to an org. */
export async function addOrgMember(
  auth: AuthContext,
  orgId: string,
  userId: string,
  role: string,
): Promise<void> {
  await fetch(`${API}/orgs/${orgId}/members`, {
    method: "POST",
    headers: auth.headers,
    body: JSON.stringify({ user_id: userId, role }),
  });
}

/** API helper: create a cohort. */
export async function createCohort(
  auth: AuthContext,
  orgId: string,
  name: string,
): Promise<string> {
  const res = await fetch(`${API}/orgs/${orgId}/cohorts`, {
    method: "POST",
    headers: auth.headers,
    body: JSON.stringify({ name }),
  });
  const data = await res.json();
  if (!data.data?.id) {
    throw new Error(`createCohort failed: ${JSON.stringify(data)}`);
  }
  return data.data.id;
}

/** API helper: add cohort member. */
export async function addCohortMember(
  auth: AuthContext,
  orgId: string,
  cohortId: string,
  userId: string,
  role = "learner",
): Promise<void> {
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}/members`, {
    method: "POST",
    headers: auth.headers,
    body: JSON.stringify({ user_id: userId, role }),
  });
}

/** API helper: activate cohort. */
export async function activateCohort(
  auth: AuthContext,
  orgId: string,
  cohortId: string,
): Promise<void> {
  await fetch(`${API}/orgs/${orgId}/cohorts/${cohortId}`, {
    method: "PUT",
    headers: auth.headers,
    body: JSON.stringify({ status: "active" }),
  });
}

/** Login via the browser UI and store auth state. */
export async function loginInBrowser(page: Page, email: string, password: string): Promise<void> {
  // Clear previous auth state (Zustand persists in localStorage)
  await page.context().clearCookies();
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.evaluate(() => {
    try { localStorage.clear(); } catch {}
    try { sessionStorage.clear(); } catch {}
  });
  await page.reload();
  await page.waitForLoadState("networkidle");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: /sign|log/i }).first().click();
  // Wait for redirect to dashboard
  await page.waitForURL("**/dashboard**", { timeout: 10_000 });
}

/** Navigate to an org's page. */
export async function goToOrg(page: Page, orgId: string): Promise<void> {
  await page.goto(`/dashboard/orgs/${orgId}`);
  await page.waitForLoadState("networkidle");
}
