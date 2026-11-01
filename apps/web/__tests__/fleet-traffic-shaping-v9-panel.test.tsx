import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficShapingV9Panel } from "@/components/fleet-traffic-shaping-v9-panel";
describe("FleetTrafficShapingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficShapingV9Panel rules={50} rpsLimit={100000} />);
    expect(container.textContent).toContain("Traffic Shaping v9");
}); });
