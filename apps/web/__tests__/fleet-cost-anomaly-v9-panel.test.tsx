import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostAnomalyV9Panel } from "@/components/fleet-cost-anomaly-v9-panel";
describe("FleetCostAnomalyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCostAnomalyV9Panel spend={50000} anomalies={0} />);
    expect(container.textContent).toContain("Cost Anomaly v9");
}); });
