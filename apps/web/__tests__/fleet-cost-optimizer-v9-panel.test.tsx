import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostOptimizerV9Panel } from "@/components/fleet-cost-optimizer-v9-panel";
describe("FleetCostOptimizerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCostOptimizerV9Panel savings={5000} applied={15} />);
    expect(container.textContent).toContain("Cost Optimizer v9");
}); });
