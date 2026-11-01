import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDeveloperPortalDashboardV9Panel } from "@/components/fleet-api-developer-portal-dashboard-v9-panel";
describe("FleetApiDeveloperPortalDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDeveloperPortalDashboardV9Panel />);
    expect(container.textContent).toContain("Dev Portal Dashboard v9");
}); });
