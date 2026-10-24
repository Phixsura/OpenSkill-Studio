import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostAnomalyPanel } from "@/components/fleet-cost-anomaly-panel";
describe("FleetCostAnomalyPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostAnomalyPanel anomaly={true} latest={500} baseline={100} ratio={5} />);
    expect(container.textContent).toContain("Cost Anomaly");
    expect(container.textContent).toContain("5x spike");
}); });
