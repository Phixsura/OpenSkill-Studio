import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PlatformDashboardPage from "@/app/(dashboard)/platform/page";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DASH = {
  period: "2026-09",
  tenants: { by_status: { active: 12, trial: 3, suspended: 1 }, total: 16 },
  mrr_minor: 500000,
  mrr_by_currency: { USD: 500000, JPY: 6000000 },
  usage: {
    by_type: [
      {
        usage_type: "model_tokens",
        currency: "EUR",
        cost_currency: "GBP",
        quantity: "120000",
        billable_minor: 40000,
        cost_minor: 12007,
        margin_minor: 26000,
      },
      {
        usage_type: "storage_gb",
        currency: "USD",
        cost_currency: "USD",
        quantity: "50",
        billable_minor: 900,
        cost_minor: 300,
        margin_minor: null,
      },
    ],
  },
  totals: {
    billable_minor: 40900,
    billable_by_currency: { EUR: 40000, USD: 900 },
    internal_cost_minor: 12300,
    cost_by_currency: { GBP: 12000, USD: 300 },
    margin_minor: 26000,
    unrated_events: 0,
    blocked_rated: 2,
  },
  credits_outstanding: [
    { currency: "USD", balance_minor: 70000, reserved_minor: 100 },
    { currency: "JPY", balance_minor: 90000, reserved_minor: 0 },
  ],
  settlement_liabilities: [{ currency: "EUR", accrued_minor: 12345 }],
  marketplace_gmv_minor: 0,
  marketplace_gmv_by_currency: {},
  attention: {
    past_due: [{ tenant_id: "t-pd", name: "Late Co", slug: "late" }],
    suspended: [],
    failed_webhooks: 3,
    dead_outbox: 1,
  },
};

beforeEach(() => vi.clearAllMocks());

describe("PlatformDashboardPage (R414)", () => {
  it("multi-currency aggregates render EVERY currency, not just the first slice", async () => {
    api.mockResolvedValue({ data: DASH });
    render(<PlatformDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Platform dashboard");
    const body = document.body.textContent ?? "";
    // MRR: full book across USD + JPY (R101[H5]); JPY is zero-decimal
    expect(body).toContain(formatMinor(500000, "USD"));
    expect(body).toContain(formatMinor(6000000, "JPY"));
    // credits outstanding: BOTH currencies (R113[H6])
    expect(body).toContain(formatMinor(70000, "USD"));
    expect(body).toContain(formatMinor(90000, "JPY"));
    // settlement liability in EUR
    expect(body).toContain(formatMinor(12345, "EUR"));
    // marketplace GMV: empty map falls back to the platform slice
    expect(body).toContain(formatMinor(0, "USD"));
  });

  it("usage economics rows carry PER-ROW currencies; margin is platform-USD or em dash", async () => {
    api.mockResolvedValue({ data: DASH });
    render(<PlatformDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Usage economics (period)");
    const body = document.body.textContent ?? "";
    expect(body).toContain(formatMinor(40000, "EUR")); // billable in EUR
    expect(body).toContain(formatMinor(12007, "GBP")); // cost in GBP (R101[H4])
    expect(body).toContain(formatMinor(26000, "USD")); // margin in USD
    expect(body).toContain("—"); // null margin row
  });

  it("attention count sums webhooks + outbox + blocked and alerts; past-due tenants link to detail", async () => {
    api.mockResolvedValue({ data: DASH });
    render(<PlatformDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Needs attention");
    // 3 + 1 + 2 = 6 in the alert card
    expect(screen.getByText("6")).toBeTruthy();
    expect(screen.getByText("3 webhooks · 1 outbox · 2 blocked")).toBeTruthy();
    expect(screen.getByText("6").closest("div")?.className).toContain("border-amber-400");
    expect(screen.getByText("Late Co").closest("a")?.getAttribute("href")).toBe(
      "/platform/tenants/t-pd",
    );
    // no suspended list when empty
    expect(screen.queryByText("Suspended")).toBeNull();
  });

  it("zero attention renders without the alert border; tenant status chips render counts", async () => {
    api.mockResolvedValue({
      data: {
        ...DASH,
        totals: { ...DASH.totals, blocked_rated: 0 },
        attention: { past_due: [], suspended: [], failed_webhooks: 0, dead_outbox: 0 },
      },
    });
    render(<PlatformDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Platform dashboard");
    expect(screen.getByText("0").closest("div")?.className).not.toContain("border-amber-400");
    expect(screen.queryByText("Needs attention")).toBeNull();
    // status chips
    expect(screen.getByText("12")).toBeTruthy();
    expect(screen.getByText("active")).toBeTruthy();
  });

  it("dashboard fetch failure renders the failure line", async () => {
    api.mockRejectedValue(new Error("dash down"));
    render(<PlatformDashboardPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Failed to load dashboard.")).toBeTruthy();
  });
});
