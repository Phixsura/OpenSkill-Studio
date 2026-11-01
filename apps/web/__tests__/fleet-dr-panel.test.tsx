import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDrPanel } from "@/components/fleet-dr-panel";
describe("FleetDrPanel", () => { it("renders", () => {
    const { container } = render(<FleetDrPanel total={5} passed={5} failed={0} lastDrillDays={30} ready={true} />);
    expect(container.textContent).toContain("DR Readiness");
    expect(container.textContent).toContain("Ready");
}); });
