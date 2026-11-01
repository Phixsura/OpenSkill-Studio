import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEndpointDiscoveryV9Panel } from "@/components/fleet-endpoint-discovery-v9-panel";
describe("FleetEndpointDiscoveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEndpointDiscoveryV9Panel endpoints={500} discovered={450} />);
    expect(container.textContent).toContain("Endpoint Discovery v9");
}); });
