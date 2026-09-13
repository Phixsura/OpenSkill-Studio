import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", cohortId: "c-1" }) }));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortSkillsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/skills/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ASSIGNED = [
  {
    cohort_id: "c-1",
    skill_id: "s-in",
    assigned_at: "2026-09-01T00:00:00Z",
    skill_name: "Prompting",
  },
  { cohort_id: "c-1", skill_id: "s-anon", assigned_at: "2026-09-01T00:00:00Z", skill_name: null },
];
const ORG_SKILLS = [
  { id: "s-in", name: "Prompting", status: "published" },
  { id: "s-out", name: "Compositing", status: "published" },
];

function route(reqs?: { path: string; method?: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    reqs?.push({
      path,
      method: init?.method,
      body: init?.body ? JSON.parse(init.body) : undefined,
    });
    if (init?.method) return Promise.resolve({ data: { ok: true } });
    if (path.includes("cohorts/c-1/skills")) return Promise.resolve({ data: ASSIGNED });
    if (path.includes("/orgs/o-1/skills")) return Promise.resolve({ data: ORG_SKILLS });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("CohortSkillsPage (R474)", () => {
  it("available section excludes already-assigned skills; null skill_name falls back to id", async () => {
    route();
    render(<CohortSkillsPage />, { wrapper: wrapper() });
    await screen.findByText("Prompting"); // assigned card
    expect(screen.getByText("s-anon")).toBeTruthy(); // name fallback
    // available offers only s-out
    expect(screen.getByText("Compositing")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "Assign" }).length).toBe(1);
    // Prompting appears once (assigned), not again as available
    expect(screen.getAllByText("Prompting").length).toBe(1);
  });

  it("Assign posts skill_id; Remove deletes by skill_id", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<CohortSkillsPage />, { wrapper: wrapper() });
    await screen.findByText("Compositing");
    fireEvent.click(screen.getByRole("button", { name: "Assign" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    const post = reqs.find((r) => r.method === "POST");
    expect(post?.path).toBe("/orgs/o-1/cohorts/c-1/skills");
    expect(post?.body).toEqual({ skill_id: "s-out" });

    fireEvent.click(screen.getAllByText("Remove")[0] as HTMLElement);
    await waitFor(() => expect(reqs.some((r) => r.method === "DELETE")).toBe(true));
    expect(reqs.find((r) => r.method === "DELETE")?.path).toBe("/orgs/o-1/cohorts/c-1/skills/s-in");
  });

  it("empty assigned state, assign-error toast, load error", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") return Promise.reject(new Error("nope"));
      if (path.includes("cohorts/c-1/skills")) return Promise.resolve({ data: [] });
      return Promise.resolve({ data: ORG_SKILLS });
    }) as typeof apiWithAuth);
    const first = render(<CohortSkillsPage />, { wrapper: wrapper() });
    expect(await first.findByText(/No skills assigned to this cohort yet/)).toBeTruthy();
    // with nothing assigned, BOTH org skills are available
    await waitFor(() => expect(screen.getAllByRole("button", { name: "Assign" }).length).toBe(2));
    fireEvent.click(screen.getAllByRole("button", { name: "Assign" })[0] as HTMLElement);
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("nope"));
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<CohortSkillsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load skills"));
  });
});
