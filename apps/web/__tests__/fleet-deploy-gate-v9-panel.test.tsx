import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeployGateV9Panel } from "@/components/fleet-deploy-gate-v9-panel";
describe("FleetDeployGateV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeployGateV9Panel total={20} blocked={0} />);
    expect(container.textContent).toContain("Deploy Gate v9");
}); });
