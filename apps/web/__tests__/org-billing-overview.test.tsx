import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgBillingOverview } from "@/components/org-billing-overview";

describe("OrgBillingOverview", () => {
  const invoices = [
    { invoice_id: "INV-001", period: "2026-10", total: 109, status: "due" },
    { invoice_id: "INV-002", period: "2026-09", total: 99, status: "paid" },
  ];
  it("renders", () => {
    const { container } = render(
      <OrgBillingOverview orgName="Acme Corp" invoices={invoices} totalPaid={99}
        totalDue={109} onViewInvoice={vi.fn()} onPay={vi.fn()} />
    );
    expect(container.textContent).toContain("Acme Corp — Billing");
    expect(container.textContent).toContain("$99.00");
    expect(container.textContent).toContain("$109.00");
    expect(container.textContent).toContain("Pay $109.00");
    expect(container.textContent).toContain("INV-001");
  });
});
