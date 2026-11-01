import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployV6Panel } from "@/components/fleet-ai-deploy-v6-panel";
describe("FleetAiDeployV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployV6Panel deployers={5} active={5} deploys={5000} rollbacks={0} lead={1} zeroDt={true} />);
    expect(container.textContent).toContain("Deploy v6");
}); });
