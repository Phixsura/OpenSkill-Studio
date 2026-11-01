import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSloWindowPanel } from "@/components/fleet-slo-window-panel";
describe("FleetSloWindowPanel", () => { it("renders", () => {
    const { container } = render(<FleetSloWindowPanel target={0.999} burnRate={2} budgetRemaining={0} alert={true} />);
    expect(container.textContent).toContain("SLO Burn Window");
    expect(container.textContent).toContain("Budget burning fast");
}); });
