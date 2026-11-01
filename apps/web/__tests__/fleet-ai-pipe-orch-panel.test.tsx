import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPipeOrchPanel } from "@/components/fleet-ai-pipe-orch-panel";
describe("FleetAiPipeOrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPipeOrchPanel orchestrators={4} active={4} pipelines={10000} stages={100000} successRate={99} />);
    expect(container.textContent).toContain("Pipeline Orchestrator");
}); });
