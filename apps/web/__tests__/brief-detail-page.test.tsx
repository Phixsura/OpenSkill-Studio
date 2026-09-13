import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const routerPush = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", briefId: "b-1" }),
  useRouter: () => ({ push: routerPush }),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});
const authState = vi.hoisted(() => ({ user: { id: "u-owner" } as { id: string } | null }));
vi.mock("@/stores/auth", () => ({
  useAuthStore: (sel: (s: { user: { id: string } | null }) => unknown) => sel(authState),
}));

import BriefDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/briefs/[briefId]/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function brief(status: string, created_by = "u-owner") {
  return {
    id: "b-1",
    title: "Hero Brief",
    client_name: "Acme",
    client_industry: null,
    project_type: "product_visualization",
    objective: "Make art",
    target_audience: null,
    tone_and_style: null,
    constraints: null,
    budget_range: null,
    timeline: null,
    deliverable_specs: [],
    evaluation_criteria: [],
    status,
    created_by,
    created_at: "2026-09-01T00:00:00Z",
  };
}

function route(
  b: Record<string, unknown>,
  posts: { path: string; body: unknown }[],
  applications: unknown[] = [],
) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      posts.push({ path, body: JSON.parse(init.body ?? "{}") });
      if (path.endsWith("/convert")) return Promise.resolve({ data: { id: "proj-9" } });
      return Promise.resolve({ data: {} });
    }
    if (path.endsWith("/applications")) return Promise.resolve({ data: applications });
    if (path.endsWith("/briefs/b-1")) return Promise.resolve({ data: b });
    return Promise.resolve({ data: null });
  }) as typeof apiWithAuth);
}

beforeEach(() => {
  vi.clearAllMocks();
  authState.user = { id: "u-owner" };
});

describe("BriefDetailPage (R456)", () => {
  it("convert (draft + owner only): posts the rubric with max_score fallback and routes to the project", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(brief("draft"), posts);
    render(<BriefDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    fireEvent.click(screen.getByRole("button", { name: /Convert to Project/ }));
    // blank the max score → the payload falls back to 100
    fireEvent.change(screen.getByPlaceholderText("Max score"), { target: { value: "" } });
    fireEvent.change(screen.getByPlaceholderText("Rubric criterion name"), {
      target: { value: "Craft" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/briefs/b-1/convert");
    expect(posts[0]?.body).toEqual({
      rubric: [{ criterion: "Craft", max_score: 100 }], // blank -> 100 fallback
    });
    await waitFor(() =>
      expect(routerPush).toHaveBeenCalledWith("/dashboard/orgs/o-1/projects/proj-9"),
    );
  });

  it("the convert affordance is hidden for non-draft briefs and the Apply box is status-gated", async () => {
    route(brief("open"), []);
    render(<BriefDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    expect(screen.queryByRole("button", { name: /Convert to Project/ })).toBeNull();
    // open brief → Apply box shows
    expect(screen.getByText("Apply to this Brief")).toBeTruthy();
  });

  it("apply posts the note; a 409 shows the already-applied toast", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(brief("open", "someone-else"), posts);
    render(<BriefDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    fireEvent.change(screen.getByPlaceholderText(/Why do you want to work on this/), {
      target: { value: "pick me" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/briefs/b-1/apply");
    expect(posts[0]?.body).toEqual({ note: "pick me" });
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Application submitted"));

    // 409 → the dedicated already-applied message
    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST")
        return Promise.reject(
          new (ApiError as new (s: number, c: string, m: string) => Error)(409, "DUP", "exists"),
        );
      if (path.endsWith("/applications")) return Promise.resolve({ data: [] });
      if (path.endsWith("/briefs/b-1")) return Promise.resolve({ data: brief("open", "x") });
      return Promise.resolve({ data: null });
    }) as typeof apiWithAuth);
    render(<BriefDetailPage />, { wrapper: wrapper() });
    const applyButtons = await screen.findAllByRole("button", { name: "Apply" });
    fireEvent.click(applyButtons[applyButtons.length - 1] as HTMLElement);
    await waitFor(() =>
      expect(toasts.error).toHaveBeenCalledWith("You have already applied to this brief."),
    );
  });

  it("an existing application shows its status chip instead of a second apply", async () => {
    route(
      brief("open", "someone-else"),
      [],
      [
        {
          id: "app-1",
          user_id: "u-owner",
          status: "submitted",
          created_at: "2026-09-01T00:00:00Z",
        },
      ],
    );
    render(<BriefDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    await waitFor(() => expect(document.body.textContent).toContain("submitted"));
  });
});
