import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PlatformPricingPage from "@/app/(dashboard)/platform/pricing/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const COST_RATE = {
  id: "cr-1",
  provider: "openai",
  model_or_service: null,
  usage_type: "model_tokens",
  currency: "USD",
  unit_cost: "0.000010",
  effective_from: "2026-01-01T00:00:00Z",
  effective_until: null,
};

const POLICIES = [
  {
    id: "pp-t",
    name: "Tenant deal",
    policy_type: "margin",
    usage_type: null,
    tenant_id: "t-1",
    partner_id: null,
    plan_version_id: null,
    currency: "USD",
    params: { margin_pct: "35" },
    is_active: true,
    effective_from: "2026-01-01T00:00:00Z",
  },
  {
    id: "pp-p",
    name: "Partner deal",
    policy_type: "margin",
    usage_type: "model_tokens",
    tenant_id: null,
    partner_id: "pt-1",
    plan_version_id: null,
    currency: "USD",
    params: {},
    is_active: true,
    effective_from: "2026-01-01T00:00:00Z",
  },
  {
    id: "pp-v",
    name: "Plan price",
    policy_type: "unit",
    usage_type: null,
    tenant_id: null,
    partner_id: null,
    plan_version_id: "pv-1",
    currency: "USD",
    params: {},
    is_active: false,
    effective_from: "2026-01-01T00:00:00Z",
  },
  {
    id: "pp-g",
    name: "Global default",
    policy_type: "unit",
    usage_type: null,
    tenant_id: null,
    partner_id: null,
    plan_version_id: null,
    currency: "USD",
    params: {},
    is_active: true,
    effective_from: "2026-01-01T00:00:00Z",
  },
];

function route(opts?: { capture?: string[]; fxEmpty?: boolean; costHasMore?: boolean }) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    opts?.capture?.push(path);
    if (path.startsWith("/platform/cost-rates"))
      return Promise.resolve({ data: [COST_RATE], meta: { has_more: opts?.costHasMore ?? false } });
    if (path.startsWith("/platform/price-policies"))
      return Promise.resolve({ data: POLICIES, meta: { has_more: false } });
    if (path.startsWith("/platform/fx-rates"))
      return Promise.resolve({
        data: opts?.fxEmpty
          ? []
          : [
              {
                id: "fx-1",
                base_currency: "EUR",
                quote_currency: "USD",
                rate: "1.0850",
                effective_from: "2026-01-01T00:00:00Z",
                effective_until: "2026-02-01T00:00:00Z",
              },
            ],
        meta: { has_more: false },
      });
    return Promise.resolve({ data: [], meta: { has_more: false } });
  });
}

beforeEach(() => {
  api.mockReset();
});

describe("PlatformPricingPage (R405)", () => {
  it("cost-rates tab is default: wildcard model, unit cost with currency, open window", async () => {
    route();
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    expect(await screen.findByText("openai")).toBeTruthy();
    expect(screen.getByText("*")).toBeTruthy(); // null model_or_service → wildcard
    expect(screen.getByText(/0\.000010 USD/)).toBeTruthy();
    expect(screen.getByText(/→\s*open/)).toBeTruthy(); // null effective_until
  });

  it("cost-rates page 2 is requested via the pager; tab switch resets to page 1", async () => {
    const capture: string[] = [];
    route({ capture, costHasMore: true });
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    await screen.findByText("openai");
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => {
      expect(capture.some((p) => p.startsWith("/platform/cost-rates?page=2"))).toBe(true);
    });
    // switch away and back — per-tab page state unmounts → back to page 1
    fireEvent.click(screen.getByRole("button", { name: "price policies" }));
    await screen.findByText("Tenant deal");
    fireEvent.click(screen.getByRole("button", { name: "cost rates" }));
    await screen.findByText("openai");
    const costCalls = capture.filter((p) => p.startsWith("/platform/cost-rates"));
    expect(costCalls[costCalls.length - 1]).toContain("page=1");
  });

  it("policies tab: scope column resolves tenant > partner > plan > global precedence", async () => {
    route();
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "price policies" }));
    await screen.findByText("Tenant deal");
    const rows = document.querySelectorAll("tbody tr");
    const scopes = Array.from(rows).map((r) => r.children[2].textContent);
    expect(scopes).toEqual(["tenant", "partner", "plan", "global"]);
    // inactive policy row is visually muted
    const inactiveRow = Array.from(rows).find((r) => r.textContent?.includes("Plan price"));
    expect(inactiveRow?.className).toContain("opacity-50");
    // params rendered as JSON
    expect(screen.getByText('{"margin_pct":"35"}')).toBeTruthy();
  });

  it("fx tab: pair + rate + closed window; empty page 1 shows the empty message", async () => {
    route();
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "fx rates" }));
    expect(await screen.findByText("EUR/USD")).toBeTruthy();
    expect(screen.getByText("1.0850")).toBeTruthy();
    expect(screen.queryByText(/→\s*open/)).toBeNull(); // has effective_until
  });

  it("fx tab empty on page 1 → 'No FX rates.'", async () => {
    route({ fxEmpty: true });
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "fx rates" }));
    expect(await screen.findByText("No FX rates.")).toBeTruthy();
  });

  it("query errors surface per-tab, not an empty table", async () => {
    api.mockImplementation(() => Promise.reject(new Error("rates down")));
    render(<PlatformPricingPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/cost rates/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
  });
});
