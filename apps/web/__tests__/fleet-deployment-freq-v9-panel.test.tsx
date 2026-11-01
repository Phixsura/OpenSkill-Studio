import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentFreqV9Panel } from "@/components/fleet-deployment-freq-v9-panel";
describe("FleetDeploymentFreqV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentFreqV9Panel teams={10} deploys={50} />);
    expect(container.textContent).toContain("Deploy Frequency v9");
}); });
