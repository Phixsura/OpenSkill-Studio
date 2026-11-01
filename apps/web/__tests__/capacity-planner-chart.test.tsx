import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityPlannerChart } from "@/components/capacity-planner-chart";

describe("CapacityPlannerChart", () => {
  it("renders forecast", () => {
    const { container } = render(
      <CapacityPlannerChart currentPct={50} capacity={1000} unit="GB"
        growthRatePct={10} exhaustionMonth={8} actionNeeded={false}
        recommendation="Monitor growth"
        projections={[
          { month: 1, usage: 550, pct: 55, exceeded: false },
          { month: 2, usage: 605, pct: 60.5, exceeded: false },
        ]} />
    );
    expect(container.textContent).toContain("Capacity Planner");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1000 GB");
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("Monitor growth");
  });
});
