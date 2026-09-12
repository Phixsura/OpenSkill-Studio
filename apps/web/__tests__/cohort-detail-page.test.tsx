import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const routerPush = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", cohortId: "c-1" }),
  useRouter: () => ({ push: routerPush }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function cohort(status: string) {
  return {
    id: "c-1",
    name: "Fall",
    description: null,
    status,
    starts_at: null,
    ends_at: null,
    max_learners: null,
    member_count: 3,
    created_at: "2026-09-01T00:00:00Z",
  };
}

const PROGRESS = {
  total_learners: 0,
  total_skills_assigned: 0,
  avg_skill_completion_pct: 0,
  overdue_submissions: 0,
  inactive_learners_7d: 0,
  projects: [],
};

function route(c: Record<string, unknown>, reqs: { method: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method && init.method !== "GET") {
      reqs.push({ method: init.method, body: init.body ? JSON.parse(init.body) : undefined });
      return Promise.resolve({ data: {} });
    }
    if (path.endsWith("/progress")) return Promise.resolve({ data: PROGRESS });
    return Promise.resolve({ data: c });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());
afterEach(() => vi.unstubAllGlobals());

describe("CohortDetailPage (R466)", () => {
  it("draft → Activate posts WITHOUT a confirm dialog", async () => {
    const reqs: { method: string; body?: unknown }[] = [];
    route(cohort("draft"), reqs);
    const confirmSpy = vi.fn(() => true);
    vi.stubGlobal("confirm", confirmSpy);
    render(<CohortDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Fall");
    fireEvent.click(screen.getByRole("button", { name: "Activate Cohort" }));
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.body).toEqual({ status: "active" });
    expect(confirmSpy).not.toHaveBeenCalled(); // activation needs no confirm
  });

  it("active → Complete REQUIRES a confirm; cancel posts nothing", async () => {
    const reqs: { method: string; body?: unknown }[] = [];
    route(cohort("active"), reqs);
    vi.stubGlobal(
      "confirm",
      vi.fn(() => false),
    ); // user cancels
    render(<CohortDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Fall");
    fireEvent.click(screen.getByRole("button", { name: "Complete Cohort" }));
    expect(reqs.length).toBe(0);
    // confirming posts completed
    vi.stubGlobal(
      "confirm",
      vi.fn(() => true),
    );
    fireEvent.click(screen.getByRole("button", { name: "Complete Cohort" }));
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.body).toEqual({ status: "completed" });
  });

  it("the next-action ladder follows the status; archived has NO next action; delete only on drafts", async () => {
    route(cohort("completed"), []);
    const r2 = render(<CohortDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Fall");
    expect(screen.getByRole("button", { name: "Archive Cohort" })).toBeTruthy();
    r2.unmount();

    vi.clearAllMocks();
    route(cohort("archived"), []);
    render(<CohortDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Fall");
    expect(screen.queryByRole("button", { name: /Activate|Complete|Archive/ })).toBeNull();
    // no Delete on a non-draft cohort
    expect(screen.queryByRole("button", { name: /Delete/ })).toBeNull();
  });
});
