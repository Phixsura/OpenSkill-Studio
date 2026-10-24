import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostOptV3Panel } from "@/components/fleet-ai-cost-opt-v3-panel";
describe("FleetAiCostOptV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostOptV3Panel optimizers={3} active={3} spend={5000000} savings={1500000} recs={100} implemented={90} roi={30} />);
    expect(container.textContent).toContain("Cost Optimizer v3");
}); });
