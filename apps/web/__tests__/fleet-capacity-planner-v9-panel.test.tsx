import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapacityPlannerV9Panel } from "@/components/fleet-capacity-planner-v9-panel";
describe("FleetCapacityPlannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCapacityPlannerV9Panel utilization={55} resources={20} />);
    expect(container.textContent).toContain("Capacity Planner v9");
}); });
