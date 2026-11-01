import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostCenterV9Panel } from "@/components/fleet-cost-center-v9-panel";
describe("FleetCostCenterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCostCenterV9Panel centers={10} spend={100000} />);
    expect(container.textContent).toContain("Cost Center v9");
}); });
