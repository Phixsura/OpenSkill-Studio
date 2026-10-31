import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDronePanel } from "@/components/fleet-drone-panel";
describe("FleetDronePanel", () => { it("renders", () => {
    const { container } = render(<FleetDronePanel total={50} success={40} failure={10} avgSteps={5} successRate={80} />);
    expect(container.textContent).toContain("Drone CI");
    expect(container.textContent).toContain("80% success");
}); });
