import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterHealthV9Panel } from "@/components/fleet-cluster-health-v9-panel";
describe("FleetClusterHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterHealthV9Panel clusters={5} nodes={250} />);
    expect(container.textContent).toContain("Cluster Health v9");
}); });
