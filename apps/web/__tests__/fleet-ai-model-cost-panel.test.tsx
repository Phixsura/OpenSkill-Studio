import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCostPanel } from "@/components/fleet-ai-model-cost-panel";
describe("FleetAiModelCostPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCostPanel trackers={4} active={4} models={200} cost={200000} costPer1k={0.001} />);
    expect(container.textContent).toContain("Model Cost");
}); });
