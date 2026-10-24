import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPipelineOrchestratorV9Panel } from "@/components/fleet-pipeline-orchestrator-v9-panel";
describe("FleetPipelineOrchestratorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPipelineOrchestratorV9Panel total={100} success={98} />);
    expect(container.textContent).toContain("Pipeline Orchestrator v9");
}); });
