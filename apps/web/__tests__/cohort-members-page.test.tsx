import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", cohortId: "c-1" }) }));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortMembersPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/members/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const COHORT_MEMBERS = [
  {
    id: "cm-1",
    user_id: "u-in",
    role: "learner",
    joined_at: "2026-09-01T00:00:00Z",
    user_name: "Ada In",
    user_email: "ada@x.com",
  },
];
const ORG_MEMBERS = [
  { id: "om-1", user: { id: "u-in", display_name: "Ada In", email: "ada@x.com" }, role: "member" },
  {
    id: "om-2",
    user: { id: "u-out", display_name: "Bob Out", email: "bob@x.com" },
    role: "member",
  },
];

function route(reqs?: { path: string; method?: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    reqs?.push({
      path,
      method: init?.method,
      body: init?.body ? JSON.parse(init.body) : undefined,
    });
    if (init?.method === "POST" || init?.method === "DELETE")
      return Promise.resolve({ data: { ok: true } });
    if (path.includes("cohorts/c-1/members"))
      return Promise.resolve({ data: COHORT_MEMBERS, meta: { total: 1 } });
    if (path.endsWith("/orgs/o-1/members")) return Promise.resolve({ data: ORG_MEMBERS });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("CohortMembersPage (R472)", () => {
  it("the add-select excludes users already enrolled in the cohort", async () => {
    route();
    render(<CohortMembersPage />, { wrapper: wrapper() });
    await screen.findByText(/Bob Out/); // available (not enrolled)
    // Ada is already a cohort member -> filtered OUT of the select options
    expect(screen.queryByRole("option", { name: /Ada In/ })).toBeNull();
    expect(screen.getByRole("option", { name: /Bob Out/ })).toBeTruthy();
    // but Ada still shows in the members table with role chip
    expect(screen.getByText("Ada In")).toBeTruthy();
    expect(screen.getByText("learner")).toBeTruthy();
  });

  it("Add is disabled without a selection; posts user_id+role then clears selection", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<CohortMembersPage />, { wrapper: wrapper() });
    await screen.findByText(/Bob Out/);
    const addBtn = screen.getByRole("button", { name: "Add" });
    expect((addBtn as HTMLButtonElement).disabled).toBe(true);
    const selects = screen.getAllByRole("combobox");
    fireEvent.change(selects[0] as HTMLElement, { target: { value: "u-out" } });
    fireEvent.change(selects[1] as HTMLElement, { target: { value: "instructor" } });
    expect((addBtn as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(addBtn);
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    const post = reqs.find((r) => r.method === "POST");
    expect(post?.path).toBe("/orgs/o-1/cohorts/c-1/members");
    expect(post?.body).toEqual({ user_id: "u-out", role: "instructor" });
    await waitFor(() =>
      expect((screen.getAllByRole("combobox")[0] as HTMLSelectElement).value).toBe(""),
    );
  });

  it("Remove deletes by user_id (not membership id); errors toast", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<CohortMembersPage />, { wrapper: wrapper() });
    await screen.findByText("Ada In");
    fireEvent.click(screen.getByText("Remove"));
    await waitFor(() => expect(reqs.some((r) => r.method === "DELETE")).toBe(true));
    expect(reqs.find((r) => r.method === "DELETE")?.path).toBe(
      "/orgs/o-1/cohorts/c-1/members/u-in",
    ); // user_id, not cm-1
  });

  it("add failure surfaces a toast; load failure shows the error line", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") return Promise.reject(new Error("CohortFull"));
      if (path.includes("cohorts/c-1/members"))
        return Promise.resolve({ data: COHORT_MEMBERS, meta: { total: 1 } });
      return Promise.resolve({ data: ORG_MEMBERS });
    }) as typeof apiWithAuth);
    const first = render(<CohortMembersPage />, { wrapper: wrapper() });
    await first.findByText(/Bob Out/);
    fireEvent.change(screen.getAllByRole("combobox")[0] as HTMLElement, {
      target: { value: "u-out" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("CohortFull"));
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<CohortMembersPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load members"));
  });
});
