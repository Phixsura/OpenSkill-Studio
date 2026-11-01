import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentVelocityV9Panel } from "@/components/fleet-deployment-velocity-v9-panel";
describe("FleetDeploymentVelocityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentVelocityV9Panel teams={10} deploys={500} />);
    expect(container.textContent).toContain("Deploy Velocity v9");
}); });
