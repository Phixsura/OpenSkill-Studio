import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLbHealthPanel } from "@/components/fleet-lb-health-panel";
describe("FleetLbHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetLbHealthPanel lbs={3} healthyBackends={19} totalBackends={20} healthPct={95} ok={true} />);
    expect(container.textContent).toContain("Load Balancers");
    expect(container.textContent).toContain("19/20");
}); });
