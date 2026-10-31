import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTrafficSplitV9Panel } from "@/components/fleet-api-traffic-split-v9-panel";
describe("FleetApiTrafficSplitV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTrafficSplitV9Panel splits={20} canaryPct={10} />);
    expect(container.textContent).toContain("Traffic Split v9");
}); });
