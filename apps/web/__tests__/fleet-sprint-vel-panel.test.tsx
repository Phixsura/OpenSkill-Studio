import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSprintVelPanel } from "@/components/fleet-sprint-vel-panel";
describe("FleetSprintVelPanel", () => { it("renders", () => {
    const { container } = render(<FleetSprintVelPanel sprints={6} avgVelocity={35} latest={40} trend="improving" />);
    expect(container.textContent).toContain("Sprint Velocity");
    expect(container.textContent).toContain("improving");
}); });
