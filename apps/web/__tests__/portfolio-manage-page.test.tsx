import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
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

import PortfolioPage from "@/app/(dashboard)/dashboard/portfolio/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const BADGES = [
  {
    id: "b-1",
    skill_name: "Prompting",
    category_name: "AI",
    completion_pct: 100,
    completed: true,
    show_on_profile: true,
  },
  {
    id: "b-2",
    skill_name: "ComfyUI",
    category_name: "AI",
    completion_pct: 40,
    completed: false,
    show_on_profile: false,
  },
];

const ITEMS = [
  {
    id: "i-1",
    title: "Chatbot",
    slug: "chatbot",
    visibility: "public",
    featured: true,
    score: 92,
    show_score: true,
  },
  {
    id: "i-2",
    title: "Hidden Score",
    slug: "hs",
    visibility: "unlisted",
    featured: false,
    score: 40,
    show_score: false,
  },
  {
    id: "i-3",
    title: "No Score",
    slug: "ns",
    visibility: "public",
    featured: false,
    score: null,
    show_score: true,
  },
];

function route(puts: { path: string; body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "PUT") {
      puts.push({ path, body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    if (path === "/portfolio/profile")
      return Promise.resolve({ data: { username: "hana", headline: null, visibility: "public" } });
    if (path === "/portfolio/items") return Promise.resolve({ data: ITEMS });
    if (path === "/portfolio/badges") return Promise.resolve({ data: BADGES });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("PortfolioPage (R419)", () => {
  it("score badge shows ONLY when show_score AND a score exists; featured chip; public link", async () => {
    route([]);
    render(<PortfolioPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    const body = document.body.textContent ?? "";
    expect(body).toContain("92/100"); // show_score + score
    expect(body).not.toContain("40/100"); // score hidden by show_score=false
    expect(screen.getByText("Featured")).toBeTruthy();
    expect(screen.getByText("openskill.studio/u/hana").getAttribute("href")).toBe("/u/hana");
    // badge meta: pct + completed marker only when completed
    expect(body).toContain("AI · 100% · completed");
    expect(body).toContain("AI · 40%");
    expect(body).not.toContain("AI · 40% · completed");
  });

  it("badge toggle PUTs show_on_profile for THAT badge id", async () => {
    const puts: { path: string; body: unknown }[] = [];
    route(puts);
    render(<PortfolioPage />, { wrapper: wrapper() });
    await screen.findByText("ComfyUI");
    fireEvent.click(screen.getByLabelText("Show ComfyUI badge on profile"));
    await waitFor(() => expect(puts.length).toBe(1));
    expect(puts[0]).toEqual({
      path: "/portfolio/badges/b-2",
      body: { show_on_profile: true },
    });
    // and unchecking the shown one sends false
    fireEvent.click(screen.getByLabelText("Show Prompting badge on profile"));
    await waitFor(() => expect(puts.length).toBe(2));
    expect(puts[1]).toEqual({
      path: "/portfolio/badges/b-1",
      body: { show_on_profile: false },
    });
  });

  it("toggle failure surfaces the API message in a toast", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "PUT")
        return Promise.reject(
          new (ApiError as new (s: number, c: string, m: string) => Error)(
            403,
            "NOT_YOURS",
            "Not your badge",
          ),
        );
      if (path === "/portfolio/badges") return Promise.resolve({ data: BADGES });
      if (path === "/portfolio/items") return Promise.resolve({ data: [] });
      return Promise.resolve({ data: null });
    }) as typeof apiWithAuth);
    render(<PortfolioPage />, { wrapper: wrapper() });
    await screen.findByText("ComfyUI");
    fireEvent.click(screen.getByLabelText("Show ComfyUI badge on profile"));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("Not your badge"));
    // empty items → empty-state hint
    expect(screen.getByText(/No portfolio items yet/)).toBeTruthy();
  });
});
