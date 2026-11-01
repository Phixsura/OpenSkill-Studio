import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQbrPanel } from "@/components/fleet-qbr-panel";
describe("FleetQbrPanel", () => { it("renders", () => {
    const { container } = render(<FleetQbrPanel quarter="Q4" target={100000} actual={120000} achievementPct={120} targetHit={true} />);
    expect(container.textContent).toContain("Q4 Review");
    expect(container.textContent).toContain("120%");
}); });
