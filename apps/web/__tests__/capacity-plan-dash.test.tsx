import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityPlanDash } from "@/components/capacity-plan-dash";

describe("CapacityPlanDash", () => {
  it("renders", () => {
    const { container } = render(
      <CapacityPlanDash current={60} capacity={100} growthRatePct={10}
        exhaustionMonth={5} actionNeeded={false}
        projections={[
          { month: 1, projectedUsage: 66, utilizationPct: 66 },
          { month: 2, projectedUsage: 72.6, utilizationPct: 72.6 },
        ]} />
    );
    expect(container.textContent).toContain("Capacity Planner");
    expect(container.textContent).toContain("+10%/mo");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("Month 1");
  });
});
