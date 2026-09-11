import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PlatformInvoicesPage from "@/app/(dashboard)/platform/invoices/page";
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

const INVOICE = {
  id: "inv-000000000001",
  number: "INV-2026-0042",
  tenant_id: "t-aaaaaaaaaa-xyz",
  status: "open",
  currency: "EUR",
  total_minor: 123456,
  amount_due_minor: 123456,
  issued_at: "2026-09-01T00:00:00Z",
  lines: [
    { id: "l-usage", line_type: "usage", description: "AI usage", amount_minor: 100000 },
    { id: "l-seat", line_type: "seat", description: "Seats", amount_minor: 23456 },
  ],
};

const TRACE = {
  line: { id: "l-usage", line_type: "usage", description: "AI usage", amount_minor: 100000 },
  invoice: { id: "inv-000000000001", number: "INV-2026-0042", tenant_id: "t-aaaaaaaaaa-xyz" },
  counts: { rated_rows: 7 },
  rated_usage: [
    {
      id: "r-1",
      usage_type: "model_tokens",
      quantity: "1200.5",
      billable_amount_minor: 100000,
      billable_currency: "EUR",
      internal_cost_minor: 40000,
      internal_cost_currency: "GBP",
      margin_minor: 51234,
      cost_rate_snapshot: { rate: "0.01" },
      sell_rate_snapshot: { rate: "0.02" },
      fx_rate_snapshot: { pair: "GBPUSD" },
      usage_event: {
        id: "u-1",
        usage_type: "model_tokens",
        quantity: "1200.5",
        occurred_at: "2026-09-01T10:00:00Z",
        source: "workflow",
        refs: {
          provider: "openai",
          model_or_service: "gpt-5",
          workflow_run_id: "run-777",
          evaluation_task_id: null,
        },
      },
    },
    {
      id: "r-2",
      usage_type: "storage_gb",
      quantity: "3",
      billable_amount_minor: 500,
      billable_currency: "EUR",
      internal_cost_minor: 100,
      internal_cost_currency: "EUR",
      margin_minor: null,
      cost_rate_snapshot: {},
      sell_rate_snapshot: {},
      fx_rate_snapshot: null,
      usage_event: null,
    },
  ],
};

function route(opts?: { fail?: boolean; hasMore?: boolean; capture?: string[] }) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    opts?.capture?.push(path);
    if (path.startsWith("/platform/invoices")) {
      if (opts?.fail) return Promise.reject(new Error("boom"));
      return Promise.resolve({ data: [INVOICE], meta: { has_more: opts?.hasMore ?? false } });
    }
    if (path.startsWith("/platform/trace/invoice-lines/")) return Promise.resolve({ data: TRACE });
    return Promise.resolve({ data: [] });
  });
}

beforeEach(() => {
  api.mockReset();
});

describe("PlatformInvoicesPage (R404)", () => {
  it("renders invoice header money in the INVOICE currency and lists lines", async () => {
    route();
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    // header total formatted in EUR — a USD hardcode would corrupt ops money
    expect(await screen.findByText(formatMinor(123456, "EUR"))).toBeTruthy();
    expect(screen.getByText("INV-2026-0042")).toBeTruthy();
    expect(screen.getByText(formatMinor(100000, "EUR"))).toBeTruthy();
    expect(screen.getByText(formatMinor(23456, "EUR"))).toBeTruthy();
  });

  it("Trace button exists ONLY on usage lines", async () => {
    route();
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    await screen.findByText("INV-2026-0042");
    const buttons = screen.getAllByRole("button", { name: "Trace" });
    expect(buttons.length).toBe(1); // seat line must NOT get a trace button
  });

  it("tenant filter is sent to the API and resets the page to 1", async () => {
    const capture: string[] = [];
    route({ capture, hasMore: true });
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    await screen.findByText("INV-2026-0042");
    // go to page 2 first
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => {
      expect(capture.some((p) => p.includes("page=2"))).toBe(true);
    });
    // typing a tenant filter must reset to page 1 AND carry tenant_id
    fireEvent.change(screen.getByPlaceholderText("Filter by tenant ID"), {
      target: { value: "t-zzz" },
    });
    await waitFor(() => {
      const last = capture[capture.length - 1];
      expect(last).toContain("tenant_id=t-zzz");
      expect(last).toContain("page=1");
    });
  });

  it("query errors render the error panel, not a silent empty list", async () => {
    route({ fail: true });
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(screen.getByText(/invoices/i)).toBeTruthy();
      expect(document.body.textContent).toMatch(/failed|error|boom/i);
    });
  });

  it("trace drawer: margin is PLATFORM-USD, null margin renders em dash, truncation note only when capped", async () => {
    route();
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    await screen.findByText("INV-2026-0042");
    fireEvent.click(screen.getByRole("button", { name: "Trace" }));
    await screen.findByText("Billing trace");
    await screen.findByText(/showing first/);
    const body = document.body.textContent ?? "";
    // margin_minor normalized to USD regardless of billable(EUR)/cost(GBP)
    expect(body).toContain(formatMinor(51234, "USD"));
    // billable in EUR, cost in GBP — per-row currencies respected
    expect(body).toContain(formatMinor(100000, "EUR"));
    expect(body).toContain(formatMinor(40000, "GBP"));
    // r-2 has null margin → em dash present
    expect(body).toContain("—");
    // counts.rated_rows(7) > rows shown(2) → truncation note
    expect(body).toContain("showing first 2 of 7 rated rows");
    // provider call refs
    expect(body).toContain("openai");
    expect(body).toContain("run run-777");
    // eval ref is null → no "eval " row for r-1
    expect(body).not.toContain("eval null");
  });

  it("trace drawer closes via the Close button", async () => {
    route();
    render(<PlatformInvoicesPage />, { wrapper: wrapper() });
    await screen.findByText("INV-2026-0042");
    fireEvent.click(screen.getByRole("button", { name: "Trace" }));
    await screen.findByText("Billing trace");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    await waitFor(() => {
      expect(screen.queryByText("Billing trace")).toBeNull();
    });
  });
});
