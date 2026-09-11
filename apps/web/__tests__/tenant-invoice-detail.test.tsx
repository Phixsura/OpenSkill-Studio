import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ tenantId: "t-1", invoiceId: "inv-1" }),
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import InvoiceDetailPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/billing/invoices/[invoiceId]/page";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
    queryCache: new QueryCache({ onError: () => {} }),
  });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const BASE = {
  id: "inv-1",
  number: "INV-0007",
  status: "paid",
  currency: "EUR",
  subtotal_minor: 100000,
  credit_applied_minor: -1500,
  total_minor: 99000,
  amount_due_minor: 0,
  issued_at: "2026-09-01T00:00:00Z",
  due_at: "2026-09-15T00:00:00Z",
  tax_minor: 500,
  paid_at: "2026-09-03T00:00:00Z",
  lines: [
    {
      id: "l-1",
      line_type: "plan",
      description: "School plan",
      quantity: "1",
      unit_amount_minor: 100000,
      amount_minor: 100000,
      usage_summary: null,
    },
  ],
  payments: [
    {
      id: "p-1",
      amount_minor: 99000,
      method: "bank_transfer",
      status: "succeeded",
      received_at: "2026-09-03T00:00:00Z",
    },
  ],
};

function route(inv: Record<string, unknown>) {
  api.mockImplementation(() => Promise.resolve({ data: inv }));
}

beforeEach(() => api.mockReset());

describe("InvoiceDetailPage (R410)", () => {
  it("renders totals in the invoice currency: subtotal, NEGATIVE credit, tax, amount due", async () => {
    route(BASE);
    render(<InvoiceDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Invoice INV-0007");
    const body = document.body.textContent ?? "";
    expect(body).toContain(formatMinor(100000, "EUR")); // subtotal + line
    // credit shown as an explicit minus of the ABSOLUTE value (backend sends -1500)
    expect(body).toContain(`−${formatMinor(1500, "EUR")}`);
    expect(body).toContain(formatMinor(500, "EUR")); // tax (R101[L5]: was dropped)
    expect(body).toContain(formatMinor(0, "EUR")); // amount due
    expect(body).toContain("Paid"); // paid_at rendered (R101[L5])
    // payment row
    expect(body).toContain("bank_transfer");
    expect(body).toContain(formatMinor(99000, "EUR"));
  });

  it("zero credit and zero tax rows are OMITTED; no payments section when empty", async () => {
    route({ ...BASE, credit_applied_minor: 0, tax_minor: 0, payments: [], paid_at: null });
    render(<InvoiceDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Invoice INV-0007");
    const body = document.body.textContent ?? "";
    expect(body).not.toContain("Credit applied");
    expect(body).not.toContain("Tax");
    expect(body).not.toContain("Payments");
    expect(body).not.toContain("Paid "); // no paid_at → no Paid line
  });

  it("missing/failed invoice renders the failure line, not a blank invoice", async () => {
    // a null payload (deleted invoice, forbidden id) must show the failure
    // line — the !invoice arm of the guard, same UI as isError
    api.mockResolvedValue({ data: null });
    render(<InvoiceDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Failed to load invoice.")).toBeTruthy();
  });
});
