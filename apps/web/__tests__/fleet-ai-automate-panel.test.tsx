import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutomatePanel } from "@/components/fleet-ai-automate-panel";
describe("FleetAiAutomatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutomatePanel workflows={20} active={20} automations={2000000} hoursSaved={20000} />);
    expect(container.textContent).toContain("AI Automation");
}); });
