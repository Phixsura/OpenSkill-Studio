import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPromptOptPanel } from "@/components/fleet-ai-prompt-opt-panel";
describe("FleetAiPromptOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPromptOptPanel optimizers={3} active={3} optimized={50000} improvement={30} tokensSaved={200000000} />);
    expect(container.textContent).toContain("Prompt Optimizer");
}); });
