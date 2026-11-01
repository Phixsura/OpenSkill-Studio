import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpotPanel } from "@/components/fleet-spot-panel";
describe("FleetSpotPanel", () => { it("renders", () => {
    const { container } = render(<FleetSpotPanel total={10} spot={7} onDemand={3} spotPct={70} costOptimized={true} />);
    expect(container.textContent).toContain("Spot Instances");
    expect(container.textContent).toContain("Cost optimized");
}); });
