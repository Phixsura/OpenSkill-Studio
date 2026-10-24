import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAgentsPanel } from "@/components/fleet-ai-agents-panel";
describe("FleetAiAgentsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAgentsPanel agents={20} running={20} tasks={200000} tools={50} />);
    expect(container.textContent).toContain("AI Agents");
}); });
