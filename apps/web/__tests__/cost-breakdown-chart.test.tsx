import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostBreakdownChart } from "@/components/cost-breakdown-chart";

describe("CostBreakdownChart", () => {
  const items = [
    { name: "API Calls", category: "compute", quantity: 100000, unit: "calls", unit_price: 0.0001, total: 10 },
    { name: "Storage", category: "storage", quantity: 50, unit: "GB", unit_price: 0.023, total: 1.15 },
  ];
  it("renders", () => {
    const { container } = render(
      <CostBreakdownChart lineItems={items} total={11.15}
        byCategory={{ compute: 10, storage: 1.15 }} largestCategory="compute" />
    );
    expect(container.textContent).toContain("Cost Breakdown");
    expect(container.textContent).toContain("$11.15");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("$10.00");
  });
});
