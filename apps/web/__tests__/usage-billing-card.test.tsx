import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageBillingCard } from "@/components/usage-billing-card";

describe("UsageBillingCard", () => {
  it("renders billing", () => {
    const { container } = render(
      <UsageBillingCard usage={5000} totalCost={20} display="$20.00"
        projectedMonthly={150000} projectedCost={520}
        breakdown={[
          { range: "1-1000", units: 1000, rate: 0, cost: 0 },
          { range: "1001-5000", units: 4000, rate: 0.005, cost: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Usage Billing");
    expect(container.textContent).toContain("$20.00");
    expect(container.textContent).toContain("5,000 units");
    expect(container.textContent).toContain("1-1000");
    expect(container.textContent).toContain("Projected");
  });
});
