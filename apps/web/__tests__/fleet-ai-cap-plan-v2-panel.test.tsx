import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCapPlanV2Panel } from "@/components/fleet-ai-cap-plan-v2-panel";
describe("FleetAiCapPlanV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCapPlanV2Panel planners={3} active={3} forecastDays={365} accuracy={95} savings={30} />);
    expect(container.textContent).toContain("Capacity Planner v2");
}); });
