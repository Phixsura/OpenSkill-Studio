import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployV8Panel } from "@/components/fleet-ai-deploy-v8-panel";
describe("FleetAiDeployV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployV8Panel deployers={5} active={5} deploys={10000} lead={1} zeroDt={true} />);
    expect(container.textContent).toContain("Deploy v8");
}); });
