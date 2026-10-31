import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerOrchestratorV9Panel } from "@/components/fleet-container-orchestrator-v9-panel";
describe("FleetContainerOrchestratorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerOrchestratorV9Panel clusters={5} cpOk={5} />);
    expect(container.textContent).toContain("Container Orchestrator v9");
}); });
