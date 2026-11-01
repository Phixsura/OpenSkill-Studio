import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiParaphrasePanel } from "@/components/fleet-ai-paraphrase-panel";
describe("FleetAiParaphrasePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiParaphrasePanel engines={3} active={3} paraphrased={10000000} quality={95} diversity={0.9} />);
    expect(container.textContent).toContain("AI Paraphraser");
}); });
