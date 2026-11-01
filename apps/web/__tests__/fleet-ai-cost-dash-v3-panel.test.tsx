import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostDashV3Panel } from "@/components/fleet-ai-cost-dash-v3-panel";
describe("FleetAiCostDashV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostDashV3Panel dashboards={3} active={3} total={5000000} savings={1000000} forecasts={200} />);
    expect(container.textContent).toContain("Cost Dashboard v3");
}); });
