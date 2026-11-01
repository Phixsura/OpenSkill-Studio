import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterSecurityV9Panel } from "@/components/fleet-cluster-security-v9-panel";
describe("FleetClusterSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterSecurityV9Panel clusters={5} score={95} />);
    expect(container.textContent).toContain("Cluster Security v9");
}); });
