import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAksPanel } from "@/components/fleet-aks-panel";
describe("FleetAksPanel", () => { it("renders", () => {
    const { container } = render(<FleetAksPanel clusters={3} running={3} nodes={50} upgradesAvailable={1} />);
    expect(container.textContent).toContain("AKS");
    expect(container.textContent).toContain("1 upgrades");
}); });
