import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTotalCostV2Panel } from "@/components/fleet-ai-total-cost-v2-panel";
describe("FleetAiTotalCostV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTotalCostV2Panel trackers={3} active={3} compute={2000000} storage={500000} network={200000} total={2700000} />);
    expect(container.textContent).toContain("Total Cost v2");
}); });
