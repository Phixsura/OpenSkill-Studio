import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterCostV9Panel } from "@/components/fleet-cluster-cost-v9-panel";
describe("FleetClusterCostV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterCostV9Panel clusters={5} total={50000} />);
    expect(container.textContent).toContain("Cluster Cost v9");
}); });
