import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRateLimitDashboardV9Panel } from "@/components/fleet-rate-limit-dashboard-v9-panel";
describe("FleetRateLimitDashboardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRateLimitDashboardV9Panel apis={50} throttled={5} />);
    expect(container.textContent).toContain("Rate Limit Dashboard v9");
}); });
