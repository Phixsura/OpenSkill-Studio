import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThroughputPlanPanel } from "@/components/throughput-plan-panel";
describe("ThroughputPlanPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ThroughputPlanPanel targetRps={1000} instancesNeeded={3} headroomPct={20}
        growthPlan={[
          { month: 1, rps: 1200, instances: 3 },
          { month: 2, rps: 1440, instances: 4 },
        ]} />
    );
    expect(container.textContent).toContain("Throughput Plan");
    expect(container.textContent).toContain("1,000 rps target");
    expect(container.textContent).toContain("3 instances");
    expect(container.textContent).toContain("20% headroom");
    expect(container.textContent).toContain("Month 1");
    expect(container.textContent).toContain("1,200 rps");
  });
});
