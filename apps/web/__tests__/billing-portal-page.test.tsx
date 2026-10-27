import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingPortalPage } from "@/components/billing-portal-page";

const sub = { planId: "pro", status: "active", currentPeriodEnd: Date.now() / 1000 + 86400 * 30 };
const invoices = [
  { invoiceId: "inv-1", amountCents: 4999, status: "paid", description: "Pro - Oct", createdAt: Date.now() },
  { invoiceId: "inv-2", amountCents: 4999, status: "pending", description: "Pro - Nov", createdAt: Date.now() },
];

describe("BillingPortalPage", () => {
  it("renders subscription and invoices", () => {
    const { container } = render(<BillingPortalPage subscription={sub} invoices={invoices} />);
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("$49.99");
    expect(container.textContent).toContain("paid");
    expect(container.textContent).toContain("Pay");
  });
  it("pay invoice", () => {
    const fn = vi.fn();
    const { container } = render(<BillingPortalPage subscription={sub} invoices={invoices} onPay={fn} />);
    const payBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Pay");
    if (payBtn) fireEvent.click(payBtn);
    expect(fn).toHaveBeenCalledWith("inv-2");
  });
});
