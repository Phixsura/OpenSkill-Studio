import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostPanel } from "@/components/fleet-ai-cost-panel";
describe("FleetAiCostPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostPanel totalMonthly={100000} gpuCost={60000} inferenceCost={40000} savings={8000} />);
    expect(container.textContent).toContain("AI Cost");
}); });
