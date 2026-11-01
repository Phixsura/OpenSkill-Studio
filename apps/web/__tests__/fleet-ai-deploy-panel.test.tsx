import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployPanel } from "@/components/fleet-ai-deploy-panel";
describe("FleetAiDeployPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployPanel pipelines={10} active={10} deployments={200} rollbacks={0} reliable={true} />);
    expect(container.textContent).toContain("AI Deploy");
    expect(container.textContent).toContain("Zero rollbacks");
}); });
