import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapacityPanel } from "@/components/fleet-capacity-panel";
describe("FleetCapacityPanel", () => { it("renders", () => {
    const { container } = render(<FleetCapacityPanel avgCpu={85} headroom={15} needsScaling={true} />);
    expect(container.textContent).toContain("Fleet Capacity");
    expect(container.textContent).toContain("Scaling needed");
}); });
