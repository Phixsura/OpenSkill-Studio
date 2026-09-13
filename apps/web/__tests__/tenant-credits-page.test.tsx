import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ tenantId: "t-1" }),
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import TenantCreditsPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/credits/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

describe("TenantCreditsPage (R381 — balances + paged ledger)", () => {
  beforeEach(() => api.mockReset());

  it("shows AVAILABLE (not raw balance) prominently and pages the ledger", async () => {
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path === "/tenants/t-1/credits") {
        return Promise.resolve({
          data: [
            { currency: "USD", balance_minor: 10000, reserved_minor: 6000, available_minor: 4000 },
          ],
        });
      }
      if (path.startsWith("/tenants/t-1/credits/ledger")) {
        const page = Number(new URLSearchParams(path.split("?")[1]).get("page"));
        return Promise.resolve({
          data: [
            {
              id: `e-${page}`,
              entry_type: "top_up",
              amount_minor: 100 * page,
              balance_after_minor: 100,
              currency: "USD",
              reference_type: null,
              reason: null,
              created_at: "2026-09-01T00:00:00Z",
            },
          ],
          meta: { has_more: page === 1 },
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<TenantCreditsPage />, { wrapper: wrapper() });
    // the headline figure is the AVAILABLE 40.00, not the raw 100.00 balance
    expect(await screen.findByText("$40.00")).toBeTruthy();
    // the M31 pagination fix: page 2 is reachable
    const next = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(next);
    await waitFor(() => {
      expect(api.mock.calls.some((c) => String(c[0]).includes("page=2"))).toBe(true);
    });
  });

  it("a failed balances fetch shows the error, never the empty state (M31)", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/tenants/t-1/credits") return Promise.reject(new Error("boom"));
      return Promise.resolve({ data: [], meta: { has_more: false } });
    });
    render(<TenantCreditsPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(screen.queryByText(/no credit balance yet/i)).toBeNull();
    });
    expect(await screen.findByText(/credit balances/i)).toBeTruthy();
  });
});
