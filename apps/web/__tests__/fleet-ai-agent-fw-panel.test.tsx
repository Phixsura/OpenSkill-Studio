import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAgentFwPanel } from "@/components/fleet-ai-agent-fw-panel";
describe("FleetAiAgentFwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAgentFwPanel frameworks={5} active={5} agents={200} tasks={5000000} />);
    expect(container.textContent).toContain("AI Agent FW");
}); });
