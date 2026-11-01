import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGovernanceDashboardV9Panel } from "@/components/fleet-api-governance-dashboard-v9-panel";
describe("FleetApiGovernanceDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGovernanceDashboardV9Panel />);
    expect(container.textContent).toContain("API Governance Dashboard v9");
}); });
