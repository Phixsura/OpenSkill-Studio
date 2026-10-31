import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BillingSummary } from "@/components/billing-summary";

describe("BillingSummary", () => {
  const plan = { name: "Pro", price: 29, interval: "monthly", status: "active" };
  const usageItems = [{ name: "API Calls", quantity: 50000, cost: 50 }];
  const invoices = [{ id: "inv_1", amount: 29, status: "paid", date: "2026-01-01" }];
  it("renders plan and usage", () => {
    const { container } = render(
      <BillingSummary plan={plan} currentUsage={50} usageItems={usageItems} invoices={invoices} />
    );
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$29/monthly");
    expect(container.textContent).toContain("$50.00");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("inv_1");
  });
});
