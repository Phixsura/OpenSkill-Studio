import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostBreakdownCard } from "@/components/cost-breakdown-card";

describe("CostBreakdownCard", () => {
  it("renders cost", () => {
    const { container } = render(
      <CostBreakdownCard plan="pro" basePrice={29} variableCost={55} total={84} display="$84.00/mo"
        lineItems={[
          { resource: "api_calls", amount: 100, rate: 0.5, cost: 50, unit: "per 1K calls" },
          { resource: "storage_gb", amount: 50, rate: 0.1, cost: 5, unit: "per GB" },
        ]} />
    );
    expect(container.textContent).toContain("Cost Estimate");
    expect(container.textContent).toContain("$84.00/mo");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("$29.00");
    expect(container.textContent).toContain("$84.00");
  });
});
