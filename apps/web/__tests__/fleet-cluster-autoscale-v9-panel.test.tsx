import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterAutoscaleV9Panel } from "@/components/fleet-cluster-autoscale-v9-panel";
describe("FleetClusterAutoscaleV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterAutoscaleV9Panel clusters={5} nodes={50} />);
    expect(container.textContent).toContain("Cluster Autoscale v9");
}); });
