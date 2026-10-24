import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficShiftPanel } from "@/components/fleet-traffic-shift-panel";
describe("FleetTrafficShiftPanel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficShiftPanel targets={2} primary="v2" primaryPct={80} />);
    expect(container.textContent).toContain("Traffic Shift");
    expect(container.textContent).toContain("v2 (80%)");
}); });
