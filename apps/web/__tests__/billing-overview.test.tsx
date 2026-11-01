import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingOverview } from "@/components/billing-overview";

describe("BillingOverview", () => {
  it("renders billing", () => {
    const { container } = render(
      <BillingOverview plan={{ name: "Pro", price: 29, interval: "monthly" }}
        currentPeriod={{ baseCost: 29, overage: 5.5, total: 34.5 }}
        usageSummary={{ apiCalls: 350000, apiLimit: 500000, apiPct: 70, storageMb: 512 }}
        paymentMethod={{ type: "card", last4: "4242", brand: "Visa" }}
        onUpgrade={vi.fn()} onManagePayment={vi.fn()} />
    );
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$34.50");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("4242");
  });
});
