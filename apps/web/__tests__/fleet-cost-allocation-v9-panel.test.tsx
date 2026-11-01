import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostAllocationV9Panel } from "@/components/fleet-cost-allocation-v9-panel";
describe("FleetCostAllocationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCostAllocationV9Panel allocations={50} total={200000} />);
    expect(container.textContent).toContain("Cost Allocation v9");
}); });
