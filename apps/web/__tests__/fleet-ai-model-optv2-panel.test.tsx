import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelOptv2Panel } from "@/components/fleet-ai-model-optv2-panel";
describe("FleetAiModelOptv2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelOptv2Panel optimizers={4} active={4} models={200} speedup={4} memReduction={50} />);
    expect(container.textContent).toContain("Model Optimizer v2");
}); });
