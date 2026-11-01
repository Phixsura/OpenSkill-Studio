import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshPolicyV9Panel } from "@/components/fleet-mesh-policy-v9-panel";
describe("FleetMeshPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMeshPolicyV9Panel total={50} enforced={50} />);
    expect(container.textContent).toContain("Mesh Policy v9");
}); });
