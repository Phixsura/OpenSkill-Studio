import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployV9Panel } from "@/components/fleet-ai-deploy-v9-panel";
describe("FleetAiDeployV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployV9Panel deployers={5} active={5} deploys={50000} lead={0.5} zeroDt={true} />);
    expect(container.textContent).toContain("Deploy v9");
}); });
