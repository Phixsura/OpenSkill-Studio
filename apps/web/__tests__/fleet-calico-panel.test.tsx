import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCalicoPanel } from "@/components/fleet-calico-panel";
describe("FleetCalicoPanel", () => { it("renders", () => {
    const { container } = render(<FleetCalicoPanel nodes={10} healthy={10} totalPolicies={80} allHealthy={true} />);
    expect(container.textContent).toContain("Calico");
    expect(container.textContent).toContain("80 network policies");
}); });
