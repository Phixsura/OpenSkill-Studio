import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostPredPanel } from "@/components/fleet-ai-cost-pred-panel";
describe("FleetAiCostPredPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostPredPanel predictors={3} active={3} predictions={5000} accuracy={95} savings={200000} />);
    expect(container.textContent).toContain("Cost Predictor");
}); });
