import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficShapePanel } from "@/components/fleet-traffic-shape-panel";
describe("FleetTrafficShapePanel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficShapePanel routes={3} active={2} totalWeight={100} balanced={false} />);
    expect(container.textContent).toContain("Traffic Shaping");
    expect(container.textContent).toContain("Weighted");
}); });
