import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentStrategyV9Panel } from "@/components/fleet-deployment-strategy-v9-panel";
describe("FleetDeploymentStrategyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentStrategyV9Panel deployments={100} rolling={70} />);
    expect(container.textContent).toContain("Deploy Strategy v9");
}); });
