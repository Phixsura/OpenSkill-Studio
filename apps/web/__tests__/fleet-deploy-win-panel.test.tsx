import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeployWinPanel } from "@/components/fleet-deploy-win-panel";
describe("FleetDeployWinPanel", () => { it("renders", () => {
    const { container } = render(<FleetDeployWinPanel total={5} inWindow={4} outWindow={1} compliant={false} />);
    expect(container.textContent).toContain("Deploy Windows");
    expect(container.textContent).toContain("1 outside");
}); });
