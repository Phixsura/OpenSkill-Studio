import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGlobalDashboardV9Panel } from "@/components/fleet-api-global-dashboard-v9-panel";
describe("FleetApiGlobalDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGlobalDashboardV9Panel />);
    expect(container.textContent).toContain("GLOBAL DASHBOARD");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
