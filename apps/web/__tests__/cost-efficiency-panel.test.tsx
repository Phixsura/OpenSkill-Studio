import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostEfficiencyPanel } from "@/components/cost-efficiency-panel";
describe("CostEfficiencyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CostEfficiencyPanel score={65} avgUtilization={45} totalCost={700}
        potentialSavings={300}
        wasteful={[{ name: "idle-vm", cost: 500, utilization: 5, potentialSavings: 300 }]} />
    );
    expect(container.textContent).toContain("Cost Efficiency");
    expect(container.textContent).toContain("Score: 65");
    expect(container.textContent).toContain("avg 45% util");
    expect(container.textContent).toContain("save $300");
    expect(container.textContent).toContain("idle-vm");
    expect(container.textContent).toContain("5% util");
  });
});
