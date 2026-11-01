import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficMirrorV9Panel } from "@/components/fleet-traffic-mirror-v9-panel";
describe("FleetTrafficMirrorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficMirrorV9Panel mirrors={10} rps={50000} />);
    expect(container.textContent).toContain("Traffic Mirror v9");
}); });
