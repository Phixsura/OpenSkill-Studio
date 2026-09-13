import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CohortsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const COHORTS = [
  {
    id: "c-1",
    name: "Fall Cohort",
    status: "active",
    description: null,
    member_count: 1,
    max_learners: 25,
    created_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "c-2",
    name: "Open Cohort",
    status: "draft",
    description: "d",
    member_count: 5,
    max_learners: null,
    created_at: "2026-09-02T00:00:00Z",
  },
];

function route(posts: { body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    if (init?.method === "POST") {
      posts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: { id: "c-new" } });
    }
    return Promise.resolve({ data: COHORTS, meta: { total: 2 } });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("CohortsPage (R464)", () => {
  it("cohort cards: status chip, member pluralization, links", async () => {
    route([]);
    render(<CohortsPage />, { wrapper: wrapper() });
    await screen.findByText("Fall Cohort");
    const body = document.body.textContent ?? "";
    expect(body).toContain("1 member");
    expect(body).not.toContain("1 members");
    expect(body).toContain("5 members");
    expect(screen.getByText("active")).toBeTruthy();
    expect(screen.getByText("Fall Cohort").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/cohorts/c-1",
    );
  });

  it("create posts trimmed-optional fields: blank optionals omitted, max cap parsed", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<CohortsPage />, { wrapper: wrapper() });
    await screen.findByText("Fall Cohort");
    fireEvent.click(screen.getByRole("button", { name: /New Cohort/ }));
    // Create disabled until a name is typed
    const createBtn = screen.getByRole("button", { name: "Create Cohort" }) as HTMLButtonElement;
    expect(createBtn.disabled).toBe(true);
    fireEvent.change(screen.getByPlaceholderText(/Cohort name/), { target: { value: "Spring" } });
    fireEvent.change(screen.getByPlaceholderText("∞"), { target: { value: "30" } });
    expect(createBtn.disabled).toBe(false);
    fireEvent.click(createBtn);
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.body).toEqual({ name: "Spring", max_learners: 30 });
    // blank description/dates OMITTED; form closes on success
    await waitFor(() => expect(screen.queryByPlaceholderText(/Cohort name/)).toBeNull());
  });

  it("empty state renders the CTA", async () => {
    api.mockResolvedValue({ data: [], meta: { total: 0 } });
    render(<CohortsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/No cohorts yet/)).toBeTruthy();
  });
});
