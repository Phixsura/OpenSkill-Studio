import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGwMeshPanel } from "@/components/fleet-gw-mesh-panel";
describe("FleetGwMeshPanel", () => { it("renders", () => {
    const { container } = render(<FleetGwMeshPanel gateways={5} healthy={5} totalRps={15000} avgP50={12} allHealthy={true} />);
    expect(container.textContent).toContain("Gateway Mesh");
    expect(container.textContent).toContain("15,000 rps");
}); });
