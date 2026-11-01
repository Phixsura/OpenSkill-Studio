import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployOrchPanel } from "@/components/fleet-ai-deploy-orch-panel";
describe("FleetAiDeployOrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployOrchPanel orchestrators={4} active={4} deployments={200} rollbackRate={1.5} deployMin={6} />);
    expect(container.textContent).toContain("Deploy Orchestrator");
}); });
