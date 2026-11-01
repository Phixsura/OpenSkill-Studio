import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceMeshSecurityV9Panel } from "@/components/fleet-service-mesh-security-v9-panel";
describe("FleetServiceMeshSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceMeshSecurityV9Panel policies={50} mtls={50} />);
    expect(container.textContent).toContain("Mesh Security v9");
}); });
