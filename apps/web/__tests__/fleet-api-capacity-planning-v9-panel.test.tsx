import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCapacityPlanningV9Panel } from "@/components/fleet-api-capacity-planning-v9-panel";
describe("FleetApiCapacityPlanningV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCapacityPlanningV9Panel apis={50} utilization={50} />);
    expect(container.textContent).toContain("Capacity Planning v9");
}); });
