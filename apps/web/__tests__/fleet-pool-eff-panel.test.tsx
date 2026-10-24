import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPoolEffPanel } from "@/components/fleet-pool-eff-panel";
describe("FleetPoolEffPanel", () => { it("renders", () => {
    const { container } = render(<FleetPoolEffPanel active={50} idle={150} efficiencyPct={25} wasteful={true} />);
    expect(container.textContent).toContain("Pool Efficiency");
    expect(container.textContent).toContain("Low pool utilization");
}); });
