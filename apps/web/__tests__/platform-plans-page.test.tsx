import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

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

import PlatformPlansPage from "@/app/(dashboard)/platform/plans/page";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PLANS = [
  {
    id: "pl-1",
    key: "school",
    name: "School",
    is_active: true,
    versions: [
      {
        id: "pv-2",
        version: 2,
        status: "draft",
        entitlements: { max_active_learners: 100 },
        prices: [{ currency: "USD", interval: "month", amount_minor: 49900 }],
      },
      {
        id: "pv-1",
        version: 1,
        status: "active",
        entitlements: { max_active_learners: 50 },
        prices: [
          { currency: "USD", interval: "month", amount_minor: 29900 },
          { currency: "JPY", interval: "year", amount_minor: 500000 },
        ],
      },
    ],
  },
];

beforeEach(() => vi.clearAllMocks());

function route(posts: string[]) {
  api.mockImplementation((rawPath: unknown, init?: { method?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      posts.push(path);
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: PLANS });
  });
}

describe("PlatformPlansPage (R416)", () => {
  it("renders per-version prices with interval; Activate exists ONLY on drafts", async () => {
    route([]);
    render(<PlatformPlansPage />, { wrapper: wrapper() });
    await screen.findByText("School");
    const body = document.body.textContent ?? "";
    expect(body).toContain(`${formatMinor(49900, "USD")}/month`);
    expect(body).toContain(`${formatMinor(29900, "USD")}/month`);
    expect(body).toContain(`${formatMinor(500000, "JPY")}/year`); // zero-decimal JPY
    // exactly one Activate (v2 draft); the active v1 must NOT get one
    expect(screen.getAllByRole("button", { name: "Activate" }).length).toBe(1);
    // entitlements JSON present
    expect(body).toContain('"max_active_learners": 100');
  });

  it("Activate posts to the DRAFT version's activate endpoint and refetches", async () => {
    const posts: string[] = [];
    route(posts);
    render(<PlatformPlansPage />, { wrapper: wrapper() });
    await screen.findByText("School");
    fireEvent.click(screen.getByRole("button", { name: "Activate" }));
    await waitFor(() => expect(posts).toEqual(["/platform/plan-versions/pv-2/activate"]));
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Version activated"));
  });

  it("New draft version posts to the plan's versions endpoint; API failure surfaces its message", async () => {
    const posts: string[] = [];
    route(posts);
    render(<PlatformPlansPage />, { wrapper: wrapper() });
    await screen.findByText("School");
    fireEvent.click(screen.getByRole("button", { name: "New draft version" }));
    await waitFor(() => expect(posts).toEqual(["/platform/plans/pl-1/versions"]));

    vi.clearAllMocks();
    api.mockImplementation((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "POST")
        return Promise.reject(
          new (ApiError as new (s: number, c: string, m: string) => Error)(
            409,
            "DRAFT_EXISTS",
            "A draft already exists",
          ),
        );
      return Promise.resolve({ data: PLANS });
    });
    fireEvent.click(screen.getByRole("button", { name: "New draft version" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("A draft already exists"));
  });

  it("a failed plans fetch renders QueryError, never a blank pane (R113[M23])", async () => {
    api.mockRejectedValue(new Error("plans down"));
    render(<PlatformPlansPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/plans/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
  });
});
