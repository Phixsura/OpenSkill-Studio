import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeployPipePanel } from "@/components/fleet-deploy-pipe-panel";
describe("FleetDeployPipePanel", () => { it("renders", () => {
    const { container } = render(<FleetDeployPipePanel total={10} passing={8} failing={2} avgDuration={12} healthy={false} />);
    expect(container.textContent).toContain("CI/CD Pipelines");
    expect(container.textContent).toContain("2 failing");
}); });
