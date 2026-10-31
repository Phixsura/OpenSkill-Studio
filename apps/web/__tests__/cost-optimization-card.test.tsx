import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostOptimizationCard } from "@/components/cost-optimization-card";

describe("CostOptimizationCard", () => {
  it("renders optimizations", () => {
    const { container } = render(
      <CostOptimizationCard totalCost={800} potentialSavings={130} savingsPct={16.3}
        recommendations={[
          { name: "idle-server", type: "compute", monthlyCost: 100, utilizationPct: 5, suggestion: "downsize_or_remove", saving: 70 },
          { name: "web-server", type: "compute", monthlyCost: 200, utilizationPct: 40, suggestion: "rightsize", saving: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Cost Optimization");
    expect(container.textContent).toContain("Save $130/mo");
    expect(container.textContent).toContain("16.3%");
    expect(container.textContent).toContain("idle-server");
    expect(container.textContent).toContain("-$70/mo");
    expect(container.textContent).toContain("5% utilized");
  });
});
