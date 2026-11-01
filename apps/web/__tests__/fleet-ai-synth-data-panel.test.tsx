import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSynthDataPanel } from "@/components/fleet-ai-synth-data-panel";
describe("FleetAiSynthDataPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSynthDataPanel generators={4} active={4} samples={20000000} quality={94} />);
    expect(container.textContent).toContain("Synthetic Data");
}); });
