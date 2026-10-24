import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployV4Panel } from "@/components/fleet-ai-deploy-v4-panel";
describe("FleetAiDeployV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployV4Panel deployers={5} active={5} deployments={1000} rollbacks={0} leadTime={3} />);
    expect(container.textContent).toContain("Deployment v4");
}); });
