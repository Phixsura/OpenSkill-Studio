import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", cohortId: "c-1" }) }));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortProjectsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/projects/page";
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
    id: "a-1",
    cohort_id: "c-1",
    project_id: "p-assigned",
    deadline_override: "2026-10-01T00:00:00Z",
    late_deadline_override: null,
    max_submissions_override: 3,
    participation_mode: "required",
    assigned_at: "2026-09-01T00:00:00Z",
    project_title: "Assigned Proj",
  },
];
const ORG_PROJECTS = [
  { id: "p-assigned", title: "Assigned Proj", status: "published" },
  { id: "p-avail", title: "Available Proj", status: "published" },
  { id: "p-draft", title: "Draft Proj", status: "draft" },
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
    if (path.includes("cohorts/c-1/projects")) return Promise.resolve({ data: ASSIGNED });
    if (path.includes("/orgs/o-1/projects")) return Promise.resolve({ data: ORG_PROJECTS });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("CohortProjectsPage (R473)", () => {
  it("assign select offers only PUBLISHED and NOT-yet-assigned projects", async () => {
    route();
    render(<CohortProjectsPage />, { wrapper: wrapper() });
    await screen.findByText("Assigned Proj");
    expect(screen.getByRole("option", { name: "Available Proj" })).toBeTruthy();
    expect(screen.queryByRole("option", { name: "Assigned Proj" })).toBeNull(); // already assigned
    expect(screen.queryByRole("option", { name: "Draft Proj" })).toBeNull(); // not published
    // assigned card shows overrides + mode
    const body = document.body.textContent ?? "";
    expect(body).toContain("Mode: required");
    expect(body).toContain("Max submissions: 3");
    expect(body).toMatch(/Deadline: /);
  });

  it("assign POST includes overrides only when set; clears form on success", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<CohortProjectsPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "Available Proj" });
    const btn = screen.getByRole("button", { name: "Assign to Cohort" });
    expect((btn as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "p-avail" } });
    fireEvent.click(btn);
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    // no overrides typed -> body carries ONLY project_id
    expect(reqs.find((r) => r.method === "POST")?.body).toEqual({ project_id: "p-avail" });
  });

  it("assign POST carries typed deadline + parsed integer max submissions", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<CohortProjectsPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "Available Proj" });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "p-avail" } });
    fireEvent.change(screen.getByPlaceholderText("Deadline override"), {
      target: { value: "2026-11-01T12:00" },
    });
    fireEvent.change(screen.getByPlaceholderText("Max submissions"), { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: "Assign to Cohort" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    expect(reqs.find((r) => r.method === "POST")?.body).toEqual({
      project_id: "p-avail",
      deadline_override: "2026-11-01T12:00",
      max_submissions_override: 5, // number, not "5"
    });
  });

  it("Remove deletes by project_id; assign error toasts", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    const first = render(<CohortProjectsPage />, { wrapper: wrapper() });
    await first.findByText("Assigned Proj");
    fireEvent.click(screen.getByText("Remove"));
    await waitFor(() => expect(reqs.some((r) => r.method === "DELETE")).toBe(true));
    expect(reqs.find((r) => r.method === "DELETE")?.path).toBe(
      "/orgs/o-1/cohorts/c-1/projects/p-assigned",
    );
    first.unmount();

    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") return Promise.reject(new Error("already assigned"));
      if (path.includes("cohorts/c-1/projects")) return Promise.resolve({ data: [] });
      return Promise.resolve({ data: ORG_PROJECTS });
    }) as typeof apiWithAuth);
    render(<CohortProjectsPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "Available Proj" });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "p-avail" } });
    fireEvent.click(screen.getByRole("button", { name: "Assign to Cohort" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("already assigned"));
  });
});
