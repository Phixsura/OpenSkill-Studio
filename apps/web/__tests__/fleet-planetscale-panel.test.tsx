import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlanetscalePanel } from "@/components/fleet-planetscale-panel";
describe("FleetPlanetscalePanel", () => { it("renders", () => {
    const { container } = render(<FleetPlanetscalePanel databases={5} production={5} deployRequests={2} rowsRead={100000000} />);
    expect(container.textContent).toContain("PlanetScale");
    expect(container.textContent).toContain("2 deploy");
}); });
