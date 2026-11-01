import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNorthStarPanel } from "@/components/fleet-north-star-panel";
describe("FleetNorthStarPanel", () => { it("renders", () => {
    const { container } = render(<FleetNorthStarPanel current={850} target={1000} achievementPct={85} onTrack={true} />);
    expect(container.textContent).toContain("North Star");
    expect(container.textContent).toContain("850");
}); });
