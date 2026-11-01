import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTopoSpreadPanel } from "@/components/fleet-topo-spread-panel";
describe("FleetTopoSpreadPanel", () => { it("renders", () => {
    const { container } = render(<FleetTopoSpreadPanel total={10} wellSpread={7} singleZone={3} resilient={false} />);
    expect(container.textContent).toContain("Topology Spread");
    expect(container.textContent).toContain("3 single-zone");
}); });
