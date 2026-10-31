import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWaypointPanel } from "@/components/fleet-waypoint-panel";
describe("FleetWaypointPanel", () => { it("renders", () => {
    const { container } = render(<FleetWaypointPanel total={10} successful={9} released={7} unreleased={2} />);
    expect(container.textContent).toContain("Waypoint");
    expect(container.textContent).toContain("2 awaiting");
}); });
