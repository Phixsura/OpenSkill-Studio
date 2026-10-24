import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RightsizeAdvisor } from "@/components/rightsize-advisor";

describe("RightsizeAdvisor", () => {
  it("renders", () => {
    const { container } = render(
      <RightsizeAdvisor totalSavings="$150.00/mo" count={2}
        recommendations={[
          { name: "idle-vm", action: "downsize_2x", savings: 120, cpuAvgPct: 5, memAvgPct: 10, monthlyCost: 200 },
          { name: "light-vm", action: "downsize_1x", savings: 30, cpuAvgPct: 25, memAvgPct: 30, monthlyCost: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Rightsizing Advisor");
    expect(container.textContent).toContain("Save $150.00/mo");
    expect(container.textContent).toContain("2 recommendations");
    expect(container.textContent).toContain("idle-vm");
    expect(container.textContent).toContain("-$120/mo");
    expect(container.textContent).toContain("CPU 5%");
  });
});
