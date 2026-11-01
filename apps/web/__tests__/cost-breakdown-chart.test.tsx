import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostBreakdownChart } from "@/components/cost-breakdown-chart";

describe("CostBreakdownChart", () => {
  it("renders costs", () => {
    const { container } = render(
      <CostBreakdownChart totalDisplay="$10,000.00"
        byTeam={[
          { team: "platform", cost: 6200, pct: 62, display: "$6,200.00" },
          { team: "data", cost: 3000, pct: 30, display: "$3,000.00" },
        ]}
        byService={[
          { service: "compute", cost: 8000, pct: 80, display: "$8,000.00" },
          { service: "storage", cost: 1200, pct: 12, display: "$1,200.00" },
        ]} />
    );
    expect(container.textContent).toContain("Cost Allocation");
    expect(container.textContent).toContain("$10,000.00");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("62%");
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("80%");
  });
});
