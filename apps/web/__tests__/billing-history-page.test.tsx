import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BillingHistoryPage } from "@/components/billing-history-page";

describe("BillingHistoryPage", () => {
  const invoices = [
    { id: "inv_1", amountDisplay: "$29.00", status: "paid", date: "2026-10-01", plan: "Pro" },
  ];
  it("renders history", () => {
    const { container } = render(
      <BillingHistoryPage invoices={invoices} totalSpentDisplay="$92.50" paid={2} total={3} />
    );
    expect(container.textContent).toContain("Billing History");
    expect(container.textContent).toContain("$92.50");
    expect(container.textContent).toContain("inv_1");
    expect(container.textContent).toContain("$29.00");
    expect(container.textContent).toContain("paid");
    expect(container.textContent).toContain("2/3");
  });
});
