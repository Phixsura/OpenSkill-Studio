import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentRolloutV9Panel } from "@/components/fleet-deployment-rollout-v9-panel";
describe("FleetDeploymentRolloutV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentRolloutV9Panel rollouts={20} complete={18} />);
    expect(container.textContent).toContain("Deploy Rollout v9");
}); });
