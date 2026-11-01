import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentWindowV9Panel } from "@/components/fleet-deployment-window-v9-panel";
describe("FleetDeploymentWindowV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentWindowV9Panel windows={10} open={5} />);
    expect(container.textContent).toContain("Deploy Window v9");
}); });
