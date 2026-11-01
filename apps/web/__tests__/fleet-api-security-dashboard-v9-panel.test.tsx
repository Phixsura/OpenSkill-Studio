import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSecurityDashboardV9Panel } from "@/components/fleet-api-security-dashboard-v9-panel";
describe("FleetApiSecurityDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSecurityDashboardV9Panel />);
    expect(container.textContent).toContain("Security Dashboard v9");
}); });
