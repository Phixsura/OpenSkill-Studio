import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPromptDefPanel } from "@/components/fleet-ai-prompt-def-panel";
describe("FleetAiPromptDefPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPromptDefPanel defenders={5} active={5} scanned={50000000} blocked={2500} fpRate={0.05} />);
    expect(container.textContent).toContain("Prompt Defense");
}); });
