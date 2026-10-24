import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapPlanPanel } from "@/components/fleet-cap-plan-panel";
describe("FleetCapPlanPanel", () => { it("renders", () => {
    const { container } = render(<FleetCapPlanPanel totalResources={20} needsExpansion={5} costDelta={10000} actionNeeded={true} />);
    expect(container.textContent).toContain("Capacity Planning");
    expect(container.textContent).toContain("+$10,000");
}); });
