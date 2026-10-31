import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostOptimizerPanel } from "@/components/cost-optimizer-panel";

describe("CostOptimizerPanel", () => {
  it("renders optimizer", () => {
    const { container } = render(
      <CostOptimizerPanel totalDisplay="$1,650/mo" savingsDisplay="$710/mo" savingsPct={43}
        recommendations={[
          { resource: "idle-server", type: "compute", action: "terminate",
            reason: "Under 20% utilization", currentCost: 500, savings: 350 },
          { resource: "db-primary", type: "database", action: "reserve",
            reason: "Switch to reserved", currentCost: 800, savings: 240 },
        ]} />
    );
    expect(container.textContent).toContain("Cost Optimizer");
    expect(container.textContent).toContain("$710/mo");
    expect(container.textContent).toContain("43%");
    expect(container.textContent).toContain("idle-server");
    expect(container.textContent).toContain("terminate");
    expect(container.textContent).toContain("db-primary");
    expect(container.textContent).toContain("reserve");
  });
});
