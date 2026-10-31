import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPromptsPanel } from "@/components/fleet-ai-prompts-panel";
describe("FleetAiPromptsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPromptsPanel registries={5} prompts={500} versions={2000} evaluations={100000} />);
    expect(container.textContent).toContain("AI Prompts");
}); });
