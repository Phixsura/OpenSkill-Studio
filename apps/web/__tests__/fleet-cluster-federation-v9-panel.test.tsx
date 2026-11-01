import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterFederationV9Panel } from "@/components/fleet-cluster-federation-v9-panel";
describe("FleetClusterFederationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterFederationV9Panel clusters={10} federated={10} />);
    expect(container.textContent).toContain("Cluster Federation v9");
}); });
