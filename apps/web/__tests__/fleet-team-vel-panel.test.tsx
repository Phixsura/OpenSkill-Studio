import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTeamVelPanel } from "@/components/fleet-team-vel-panel";
describe("FleetTeamVelPanel", () => { it("renders", () => {
    const { container } = render(<FleetTeamVelPanel teams={5} totalPoints={200} avgVelocity={40} topTeam="alpha" />);
    expect(container.textContent).toContain("Team Velocity");
    expect(container.textContent).toContain("alpha");
}); });
