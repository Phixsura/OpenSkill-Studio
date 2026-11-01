import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingInvoiceViewer } from "@/components/billing-invoice-viewer";

const mockInvoice = {
  invoiceId: "INV-2026-042", period: "October 2026", status: "pending" as const,
  issuedAt: "Oct 1, 2026", dueAt: "Oct 31, 2026", currency: "USD",
  lineItems: [
    { description: "Slack Bot Pro (Monthly)", quantity: 1, unitPrice: 999, total: 999 },
    { description: "API Overage (5,000 calls)", quantity: 5000, unitPrice: 1, total: 5000 },
  ],
  subtotal: 5999, tax: 540, total: 6539,
};

describe("BillingInvoiceViewer", () => {
  it("renders invoice details", () => {
    const { container } = render(<BillingInvoiceViewer invoice={mockInvoice} />);
    expect(container.textContent).toContain("INV-2026-042");
    expect(container.textContent).toContain("October 2026");
    expect(container.textContent).toContain("Pending");
    expect(container.textContent).toContain("$65.39");
  });

  it("renders line items", () => {
    const { container } = render(<BillingInvoiceViewer invoice={mockInvoice} />);
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("API Overage");
    expect(container.textContent).toContain("$9.99");
  });

  it("shows Pay Now for pending", () => {
    const onPay = vi.fn();
    const { getByText } = render(<BillingInvoiceViewer invoice={mockInvoice} onPay={onPay} />);
    fireEvent.click(getByText("💳 Pay Now"));
    expect(onPay).toHaveBeenCalled();
  });

  it("hides Pay Now for paid invoices", () => {
    const paid = { ...mockInvoice, status: "paid" as const };
    const { container } = render(<BillingInvoiceViewer invoice={paid} onPay={() => {}} />);
    expect(container.textContent).not.toContain("Pay Now");
    expect(container.textContent).toContain("Paid");
  });
});
