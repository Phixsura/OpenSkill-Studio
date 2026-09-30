import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const searchParams = { current: new URLSearchParams() };

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/catalog",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => searchParams.current,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BenchmarksPage from "@/app/(dashboard)/dashboard/ecosystem/benchmarks/page";
import CatalogPage from "@/app/(dashboard)/dashboard/ecosystem/catalog/page";
import ComparePage from "@/app/(dashboard)/dashboard/ecosystem/compare/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ENTITY_ID = "E".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  searchParams.current = new URLSearchParams();
  api.mockResolvedValue({ data: [], meta: { total: 0 } });
});

describe("Ecosystem deep links & failure surfacing (ADR-016 §66)", () => {
  it("catalog restores the Inspect panel from ?kind=&entity=", async () => {
    searchParams.current = new URLSearchParams(`kind=models&entity=${ENTITY_ID}`);
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/catalog/models?"))
        return Promise.resolve({
          data: [
            {
              id: ENTITY_ID,
              canonical_name: "DeepLinkGen",
              lifecycle_status: "verified",
              created_at: "2026-09-20T00:00:00Z",
              sunset_at: null,
            },
          ],
          meta: { total: 1 },
        });
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    // The Inspect panel opens without any click — restored from the URL
    expect(await screen.findByText(/Source conflicts for DeepLinkGen/)).toBeDefined();
  });

  it("estimator surfaces API errors instead of swallowing them", async () => {
    const { ApiError } = await import("@/lib/api");
    const ApiErrorCtor = ApiError as unknown as new (message: string) => Error;
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/pricing/estimate")
        return Promise.reject(new ApiErrorCtor("Unknown price unit: gpu_hour"));
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: ENTITY_ID },
    });
    fireEvent.click(screen.getByText("Estimate cost"));
    expect(await screen.findByText(/Unknown price unit|failed/)).toBeDefined();
  });

  it("failed runs show their machine error class inline", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/benchmark/runs?"))
        return Promise.resolve({
          data: [
            {
              id: "R".repeat(26),
              error: "ECO_BUDGET_EXCEEDED: run aborted at budget cap",
              status: "failed",
              target: { entity_kind: "model", entity_id: ENTITY_ID },
              total_cost_usd: 10,
              dimension_scores: {},
              created_at: "2026-09-20T00:00:00Z",
            },
          ],
        });
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<BenchmarksPage />, { wrapper: wrapper() });
    expect(await screen.findByText("ECO_BUDGET_EXCEEDED")).toBeDefined();
  });
});
