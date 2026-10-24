import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostOptPanel } from "@/components/fleet-ai-cost-opt-panel";
describe("FleetAiCostOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostOptPanel optimizers={3} active={3} spend={100000} savings={35000} savingsPct={26} />);
    expect(container.textContent).toContain("Cost Optimizer");
}); });
