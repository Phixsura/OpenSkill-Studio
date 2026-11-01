import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingPageLayout } from "@/components/billing-page-layout";

describe("BillingPageLayout", () => {
  it("renders billing", () => {
    const { container } = render(
      <BillingPageLayout planName="pro" planPrice="$99/mo" renewalDate="2026-11-01"
        currentSpend="$99.00" hasPaymentMethod={true} paymentLast4="4242"
        alerts={{ past_due: false, near_limit: false }} onUpgrade={vi.fn()} onAddPayment={vi.fn()}>
        <p>Invoices</p>
      </BillingPageLayout>
    );
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("$99.00");
    expect(container.textContent).toContain("4242");
    expect(container.textContent).toContain("Invoices");
  });
  it("past due alert", () => {
    const { container } = render(
      <BillingPageLayout planName="x" planPrice="" renewalDate={null} currentSpend="$0"
        hasPaymentMethod={false} alerts={{ past_due: true, near_limit: false }}
        onUpgrade={vi.fn()} onAddPayment={vi.fn()}>
        <p>C</p>
      </BillingPageLayout>
    );
    expect(container.textContent).toContain("past-due");
    expect(container.textContent).toContain("Add Payment");
  });
});
