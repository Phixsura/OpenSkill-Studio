import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", projectId: "p-1" }) }));
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

import CreatorShortlistPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/[projectId]/shortlist/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PROFILES = {
  data: [
    {
      id: "prof-1",
      context_type: "production",
      status: "confirmed",
      structured_requirements: { goal: "Make a hero image" },
    },
    {
      id: "prof-2",
      context_type: "production",
      status: "draft", // draft excluded
      structured_requirements: { goal: "Draft goal" },
    },
  ],
  meta: { has_more: false },
};

const SHORTLIST = {
  match_run_id: "run-42",
  results: [
    {
      entity_id: "u-1",
      name: "Ada",
      rank: 1,
      score: 0.9,
      tier: "great",
      reasons: [{ code: "r1", label: "Strong evidence" }],
      gaps: [{ code: "g1", label: "No video work" }],
      evidence: {},
    },
    {
      entity_id: "u-2",
      name: "Bob",
      rank: 2,
      score: 0.5,
      tier: "fair",
      reasons: [],
      gaps: [],
      evidence: {},
    },
  ],
  excluded: [],
};

function route(opts?: { posts?: { path: string; body: unknown }[]; assignments?: unknown[] }) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      if (path.includes("creator-shortlist")) return Promise.resolve({ data: SHORTLIST });
      opts?.posts?.push({ path, body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: { id: "a-new" } });
    }
    if (path.includes("creator-shortlist")) return Promise.resolve({ data: SHORTLIST });
    if (path.includes("requirement-profiles")) return Promise.resolve(PROFILES);
    if (path.includes("creator-assignments"))
      return Promise.resolve({ data: opts?.assignments ?? [] });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("CreatorShortlistPage (R453)", () => {
  it("only CONFIRMED profiles appear in the select", async () => {
    route();
    render(<CreatorShortlistPage />, { wrapper: wrapper() });
    await screen.findByText("Creator Shortlist");
    await waitFor(() => expect(screen.getByText(/Make a hero image/)).toBeTruthy());
    // the draft profile is filtered out
    expect(screen.queryByText(/Draft goal/)).toBeNull();
  });

  it("build shortlist renders ranked creators with tier + reasons/gaps", async () => {
    route();
    render(<CreatorShortlistPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/Make a hero image/)).toBeTruthy());
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "prof-1" } });
    fireEvent.click(screen.getByRole("button", { name: /Build Shortlist/ }));
    await screen.findByText("Ada");
    const body = document.body.textContent ?? "";
    expect(body).toContain("Bob");
    expect(body).toContain("Strong evidence"); // reason chip
    expect(body).toContain("No video work"); // gap chip
  });

  it("two-click assign posts the offer with the match_run_id", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route({ posts });
    render(<CreatorShortlistPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/Make a hero image/)).toBeTruthy());
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "prof-1" } });
    fireEvent.click(screen.getByRole("button", { name: /Build Shortlist/ }));
    await screen.findByText("Ada");

    // first click ARMS (shows "Confirm offer?"), does NOT post yet
    fireEvent.click(screen.getAllByRole("button", { name: "Assign" })[0] as HTMLElement);
    expect(await screen.findByRole("button", { name: "Confirm offer?" })).toBeTruthy();
    expect(posts.length).toBe(0);
    // confirm posts the offer with project + user + match_run_id
    fireEvent.click(screen.getByRole("button", { name: "Confirm offer?" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/creator-assignments");
    expect(posts[0]?.body).toEqual({ project_id: "p-1", user_id: "u-1", match_run_id: "run-42" });
    await waitFor(() => expect(toasts.success).toHaveBeenCalled());
  });

  it("already-offered creators show 'Already offered' instead of an Assign button", async () => {
    route({
      assignments: [
        { id: "a-1", user_id: "u-1", status: "offered", created_at: "2026-09-01T00:00:00Z" },
      ],
    });
    render(<CreatorShortlistPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/Make a hero image/)).toBeTruthy());
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "prof-1" } });
    fireEvent.click(screen.getByRole("button", { name: /Build Shortlist/ }));
    await screen.findByText("Ada");
    // u-1 already offered → "Already offered"; only u-2 gets an Assign button
    expect(screen.getByText("Already offered")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "Assign" }).length).toBe(1);
  });
});
