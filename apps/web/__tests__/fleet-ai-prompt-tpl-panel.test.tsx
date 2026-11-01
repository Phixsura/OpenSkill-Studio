import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPromptTplPanel } from "@/components/fleet-ai-prompt-tpl-panel";
describe("FleetAiPromptTplPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPromptTplPanel libraries={3} active={3} templates={1000} uses={10000000} tokensSaved={500000000} />);
    expect(container.textContent).toContain("Prompt Templates");
}); });
