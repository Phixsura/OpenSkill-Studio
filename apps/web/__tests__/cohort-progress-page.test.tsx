import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", cohortId: "c-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortProgressPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/progress/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const STATS = {
  total_learners: 12,
  total_skills_assigned: 4,
  avg_skill_completion_pct: 62.5,
  overdue_submissions: 3,
  inactive_learners_7d: 2,
  projects: [],
};

function route(stats: Record<string, unknown> | null, learners: unknown[]) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.endsWith("/progress")) return Promise.resolve({ data: stats });
    if (path.includes("/members"))
      return Promise.resolve({ data: learners, meta: { total: learners.length } });
    return Promise.resolve({ data: null });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("CohortProgressPage (R449)", () => {
  it("aggregate stat tiles render the progress numbers with the % suffix", async () => {
    route(STATS, []);
    render(<CohortProgressPage />, { wrapper: wrapper() });
    await screen.findByText("62.5%"); // wait for the stats query to resolve
    const body = document.body.textContent ?? "";
    expect(body).toContain("12"); // learners
    expect(body).toContain("62.5%"); // avg skill completion with % suffix
    expect(body).toContain("3"); // overdue
    expect(body).toContain("2"); // inactive
    // the members request filters to learners with a large page size
    const calls = api.mock.calls.map((c) => String(c[0]));
    expect(calls.some((p) => p.includes("role=learner") && p.includes("per_page=100"))).toBe(true);
  });

  it("learner rows link to the per-learner drilldown; name falls back to id", async () => {
    route(STATS, [
      {
        id: "m1",
        user_id: "u-1",
        role: "learner",
        user_name: "Ada",
        joined_at: "2026-08-01T00:00:00Z",
      },
      {
        id: "m2",
        user_id: "u-2",
        role: "learner",
        user_name: null,
        joined_at: "2026-08-02T00:00:00Z",
      },
    ]);
    render(<CohortProgressPage />, { wrapper: wrapper() });
    await screen.findByText("Ada");
    expect(screen.getByText("Ada").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/cohorts/c-1/progress/u-1",
    );
    // null name falls back to the user id
    expect(screen.getByText("u-2")).toBeTruthy();
  });

  it("empty learners -> enrolled-yet message; members error -> retry line", async () => {
    route(STATS, []);
    render(<CohortProgressPage />, { wrapper: wrapper() });
    expect(await screen.findByText("No learners enrolled yet.")).toBeTruthy();

    vi.clearAllMocks();
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith("/progress")) return Promise.resolve({ data: STATS });
      return Promise.reject(new Error("members down"));
    });
    render(<CohortProgressPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load learner list/));
  });
});
