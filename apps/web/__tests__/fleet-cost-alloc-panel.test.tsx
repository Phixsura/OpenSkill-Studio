import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostAllocPanel } from "@/components/fleet-cost-alloc-panel";
describe("FleetCostAllocPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostAllocPanel totalCost={1000} topSpender="platform" />);
    expect(container.textContent).toContain("Cost Allocation");
    expect(container.textContent).toContain("platform");
}); });
