import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTrafficControlV9Panel } from "@/components/fleet-api-traffic-control-v9-panel";
describe("FleetApiTrafficControlV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTrafficControlV9Panel controls={10} rps={1000000} />);
    expect(container.textContent).toContain("Traffic Control v9");
}); });
