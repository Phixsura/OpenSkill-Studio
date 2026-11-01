import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshPolicyPanel } from "@/components/fleet-mesh-policy-panel";
describe("FleetMeshPolicyPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeshPolicyPanel total={10} withPolicy={10} defaultDeny={10} zeroTrust={true} />);
    expect(container.textContent).toContain("Mesh Policies");
    expect(container.textContent).toContain("Zero Trust");
}); });
