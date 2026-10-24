import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChangeVelPanel } from "@/components/fleet-change-vel-panel";
describe("FleetChangeVelPanel", () => { it("renders", () => {
    const { container } = render(<FleetChangeVelPanel deploys={50} hours={24} ratePerHour={2.08} highVelocity={true} />);
    expect(container.textContent).toContain("Change Velocity");
    expect(container.textContent).toContain("High velocity");
}); });
