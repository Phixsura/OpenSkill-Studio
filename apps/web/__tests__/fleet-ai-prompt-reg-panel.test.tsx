import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPromptRegPanel } from "@/components/fleet-ai-prompt-reg-panel";
describe("FleetAiPromptRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPromptRegPanel registries={3} active={3} templates={500} versions={2000} />);
    expect(container.textContent).toContain("Prompt Registry");
}); });
