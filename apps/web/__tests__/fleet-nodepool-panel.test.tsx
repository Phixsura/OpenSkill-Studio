import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNodepoolPanel } from "@/components/fleet-nodepool-panel";
describe("FleetNodepoolPanel", () => { it("renders", () => {
    const { container } = render(<FleetNodepoolPanel pools={3} totalNodes={15} capacity={30} utilPct={50} atMax={1} />);
    expect(container.textContent).toContain("Node Pools");
    expect(container.textContent).toContain("1 pools at max");
}); });
