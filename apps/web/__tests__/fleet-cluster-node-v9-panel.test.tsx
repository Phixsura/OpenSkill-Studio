import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterNodeV9Panel } from "@/components/fleet-cluster-node-v9-panel";
describe("FleetClusterNodeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterNodeV9Panel nodes={50} ready={50} />);
    expect(container.textContent).toContain("Cluster Node v9");
}); });
