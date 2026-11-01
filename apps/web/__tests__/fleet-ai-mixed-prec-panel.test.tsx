import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMixedPrecPanel } from "@/components/fleet-ai-mixed-prec-panel";
describe("FleetAiMixedPrecPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMixedPrecPanel configs={5} active={5} speedup={3} memReduction={55} precisions={["FP16", "BF16"]} />);
    expect(container.textContent).toContain("Mixed Precision");
}); });
