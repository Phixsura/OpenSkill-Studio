import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostV5Panel } from "@/components/fleet-ai-cost-v5-panel";
describe("FleetAiCostV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostV5Panel trackers={3} active={3} total={20000000} savings={8000000} savingsPct={28.6} forecastAcc={97} />);
    expect(container.textContent).toContain("AI Cost v5");
}); });
