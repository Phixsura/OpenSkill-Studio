import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPerformanceDashboardV9Panel } from "@/components/fleet-api-performance-dashboard-v9-panel";
describe("FleetApiPerformanceDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPerformanceDashboardV9Panel />);
    expect(container.textContent).toContain("Performance Dashboard v9");
}); });
