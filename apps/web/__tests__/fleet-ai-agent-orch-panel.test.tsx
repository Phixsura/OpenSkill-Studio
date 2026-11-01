import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAgentOrchPanel } from "@/components/fleet-ai-agent-orch-panel";
describe("FleetAiAgentOrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAgentOrchPanel orchestrators={3} active={3} agents={100} tasks={500000} successRate={99.5} />);
    expect(container.textContent).toContain("Agent Orchestrator");
}); });
