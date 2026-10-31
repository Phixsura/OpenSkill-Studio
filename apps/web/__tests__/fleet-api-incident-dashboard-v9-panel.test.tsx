import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiIncidentDashboardV9Panel } from "@/components/fleet-api-incident-dashboard-v9-panel";
describe("FleetApiIncidentDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiIncidentDashboardV9Panel incidents={50} open={0} />);
    expect(container.textContent).toContain("Incident Dashboard v9");
}); });
