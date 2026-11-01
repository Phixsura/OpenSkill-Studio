import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpCostPanel } from "@/components/ep-cost-panel";
describe("EpCostPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpCostPanel totalCost={1000}
        endpoints={[
          { endpoint: "/users", cost: 700, costPer1k: 0.07, sharePct: 70 },
          { endpoint: "/reports", cost: 300, costPer1k: 3.0, sharePct: 30 },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Costs");
    expect(container.textContent).toContain("$1,000 total");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("$700");
    expect(container.textContent).toContain("70%");
  });
});
