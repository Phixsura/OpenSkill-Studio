import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEpHealthPanel } from "@/components/fleet-ep-health-panel";
describe("FleetEpHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetEpHealthPanel total={10} up={9} degraded={1} down={0} availabilityPct={90} />);
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("90%");
}); });
