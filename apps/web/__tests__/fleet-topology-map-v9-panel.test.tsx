import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTopologyMapV9Panel } from "@/components/fleet-topology-map-v9-panel";
describe("FleetTopologyMapV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTopologyMapV9Panel nodes={100} connections={500} />);
    expect(container.textContent).toContain("Topology Map v9");
}); });
