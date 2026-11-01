import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostV8Panel } from "@/components/fleet-ai-cost-v8-panel";
describe("FleetAiCostV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostV8Panel trackers={3} active={3} spend={100000000} savings={40000000} costPerReq={0.0000005} roi={40} />);
    expect(container.textContent).toContain("Cost v8");
}); });
