import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSysPromptPanel } from "@/components/fleet-ai-sys-prompt-panel";
describe("FleetAiSysPromptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSysPromptPanel managers={3} active={3} prompts={200} versions={1000} uses={50000000} />);
    expect(container.textContent).toContain("System Prompt");
}); });
