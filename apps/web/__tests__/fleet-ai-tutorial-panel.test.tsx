import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTutorialPanel } from "@/components/fleet-ai-tutorial-panel";
describe("FleetAiTutorialPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTutorialPanel engines={2} active={2} tutorials={500} completions={50000} rating={4.9} />);
    expect(container.textContent).toContain("AI Tutorials");
}); });
