import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ tenantId: "t-1" }),
}));
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import TenantBudgetsPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/budgets/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route(overrides: { currency?: string | null; budgets?: unknown[] } = {}) {
  api.mockImplementation((path: string) => {
    if (path === "/tenants/t-1/budgets") {
      return Promise.resolve({ data: overrides.budgets ?? [] });
    }
    if (path === "/tenants/t-1") {
      return Promise.resolve({
        data: overrides.currency === null ? {} : { currency: overrides.currency ?? "JPY" },
      });
    }
    return Promise.resolve({ data: {} });
  });
}

describe("TenantBudgetsPage (R380 — the R101[H8]/R113[M26] money form)", () => {
  beforeEach(() => api.mockReset());

  it("creates the budget in the TENANT currency with zero-decimal minor math", async () => {
    route({ currency: "JPY" });
    render(<TenantBudgetsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /new budget/i }));
    const limit = await screen.findByPlaceholderText(/limit/i);
    fireEvent.change(limit, { target: { value: "5000" } });
    fireEvent.click(screen.getByRole("button", { name: /^create$/i }));
    await waitFor(() => {
      const post = api.mock.calls.find(
        (c) => c[0] === "/tenants/t-1/budgets" && (c[1] as RequestInit)?.method === "POST",
      );
      expect(post).toBeTruthy();
      const body = JSON.parse((post![1] as RequestInit).body as string);
      // JPY is zero-decimal: 5000 major → 5000 minor (the ×100 bug = 500000)
      expect(body.limit_minor).toBe(5000);
      expect(body.currency).toBe("JPY");
      expect(body.scope_type).toBe("tenant");
      expect(body.scope_id).toBeNull();
    });
  });

  it("blocks Create while the tenant currency is unknown (R113[M26])", async () => {
    route({ currency: null });
    render(<TenantBudgetsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /new budget/i }));
    const create = (await screen.findByRole("button", {
      name: /create/i,
    })) as HTMLButtonElement;
    await waitFor(() => expect(create.disabled).toBe(true));
    // fill a valid limit — the button must STILL be disabled (currency gate)
    fireEvent.change(await screen.findByPlaceholderText(/limit/i), {
      target: { value: "100" },
    });
    await waitFor(() => expect(create.disabled).toBe(true));
    fireEvent.click(create);
    const post = api.mock.calls.find((c) => (c[1] as RequestInit | undefined)?.method === "POST");
    expect(post).toBeUndefined(); // never fell back to USD
  });

  it("renders existing budgets with formatted limits and deletes by id", async () => {
    route({
      currency: "USD",
      budgets: [
        {
          id: "b-9",
          scope_type: "org",
          scope_id: "o-1",
          period: "monthly",
          capability_key: null,
          usage_type: null,
          limit_minor: 12345,
          currency: "USD",
          warning_threshold_pct: 80,
          hard_stop: true,
          is_active: true,
        },
      ],
    });
    render(<TenantBudgetsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/123\.45|\$123\.45/)).toBeTruthy();
    const del = screen.getByRole("button", { name: /remove|delete/i });
    fireEvent.click(del);
    await waitFor(() => {
      const call = api.mock.calls.find(
        (c) => c[0] === "/tenants/t-1/budgets/b-9" && (c[1] as RequestInit)?.method === "DELETE",
      );
      expect(call).toBeTruthy();
    });
  });
});
