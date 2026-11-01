import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityPlannerWidget } from "@/components/capacity-planner-widget";

describe("CapacityPlannerWidget", () => {
  it("renders planner", () => {
    const { container } = render(
      <CapacityPlannerWidget current={60} growthRate={10} monthsToLimit={5}
        needsExpansion={true}
        recommendation={{ action: "scale_up", urgency: "high", recommendedCapacity: 200 }}
        projections={[
          { month: 1, usage: 66, pctOfCapacity: 66 },
          { month: 2, usage: 73, pctOfCapacity: 73 },
        ]} />
    );
    expect(container.textContent).toContain("Capacity Planner");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("Limit in 5mo");
    expect(container.textContent).toContain("scale_up");
    expect(container.textContent).toContain("M1");
  });
});
