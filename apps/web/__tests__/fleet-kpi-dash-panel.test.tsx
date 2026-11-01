import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKpiDashPanel } from "@/components/fleet-kpi-dash-panel";
describe("FleetKpiDashPanel", () => { it("renders", () => {
    const { container } = render(<FleetKpiDashPanel uptimePct={99.95} userGrowth={15} revenueGrowth={25} healthy={true} />);
    expect(container.textContent).toContain("Platform KPIs");
    expect(container.textContent).toContain("+25%");
}); });
