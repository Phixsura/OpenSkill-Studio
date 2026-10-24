import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceTopologyV9Panel } from "@/components/fleet-service-topology-v9-panel";
describe("FleetServiceTopologyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceTopologyV9Panel nodes={200} edges={600} />);
    expect(container.textContent).toContain("Service Topology v9");
}); });
