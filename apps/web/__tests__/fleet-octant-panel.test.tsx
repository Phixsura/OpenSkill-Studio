import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOctantPanel } from "@/components/fleet-octant-panel";
describe("FleetOctantPanel", () => { it("renders", () => {
    const { container } = render(<FleetOctantPanel totalSessions={30} active={15} clustersViewed={5} />);
    expect(container.textContent).toContain("Octant");
    expect(container.textContent).toContain("5 clusters");
}); });
