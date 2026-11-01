import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostSumPanel } from "@/components/fleet-cost-sum-panel";
describe("FleetCostSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostSumPanel totalCost={600} avgCost={200} services={3} />);
    expect(container.textContent).toContain("Fleet Cost");
    expect(container.textContent).toContain("$600 total");
}); });
