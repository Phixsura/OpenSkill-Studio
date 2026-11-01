import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostTrendPanel } from "@/components/fleet-cost-trend-panel";
describe("FleetCostTrendPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostTrendPanel trend="increasing" changePct={20} latest={12000} />);
    expect(container.textContent).toContain("Cost Trend");
    expect(container.textContent).toContain("+20%");
}); });
