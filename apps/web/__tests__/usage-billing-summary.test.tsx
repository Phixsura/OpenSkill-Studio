import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageBillingSummary } from "@/components/usage-billing-summary";

describe("UsageBillingSummary", () => {
  it("renders billing", () => {
    const { container } = render(
      <UsageBillingSummary apiCalls={150000} apiCost={50} storageGb={50}
        storageCost={5} basePrice={29} totalDisplay="$84.00"
        breakdown={[
          { range: "0-10,000", calls: 10000, rate: 0, cost: 0 },
          { range: "10,000-100,000", calls: 90000, rate: 0.001, cost: 90 },
        ]} />
    );
    expect(container.textContent).toContain("Usage Billing");
    expect(container.textContent).toContain("$84.00");
    expect(container.textContent).toContain("150,000");
    expect(container.textContent).toContain("50 GB");
    expect(container.textContent).toContain("Tier Breakdown");
  });
});
