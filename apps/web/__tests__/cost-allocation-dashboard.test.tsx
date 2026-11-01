import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAllocationDashboard } from "@/components/cost-allocation-dashboard";

describe("CostAllocationDashboard", () => {
  it("renders allocations", () => {
    const { container } = render(
      <CostAllocationDashboard totalCost="$1,000.00" trend="up" pctChange={20}
        byTeam={{ platform: 800, data: 200 }}
        byProject={{ api: 500, web: 300, pipeline: 200 }} />
    );
    expect(container.textContent).toContain("Cost Allocation");
    expect(container.textContent).toContain("$1,000.00");
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("$800");
    expect(container.textContent).toContain("api");
  });
});
