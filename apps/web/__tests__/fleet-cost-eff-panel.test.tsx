import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostEffPanel } from "@/components/fleet-cost-eff-panel";
describe("FleetCostEffPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostEffPanel ratio={10} grade="A" revenue={100000} infraCost={10000} />);
    expect(container.textContent).toContain("Cost Efficiency");
    expect(container.textContent).toContain("10x — A");
}); });
