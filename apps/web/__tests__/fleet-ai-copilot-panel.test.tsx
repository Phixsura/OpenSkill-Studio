import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCopilotPanel } from "@/components/fleet-ai-copilot-panel";
describe("FleetAiCopilotPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCopilotPanel copilots={10} active={10} interactions={10000000} satisfaction={94} />);
    expect(container.textContent).toContain("AI Copilot");
}); });
