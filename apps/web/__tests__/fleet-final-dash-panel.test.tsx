import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFinalDashPanel } from "@/components/fleet-final-dash-panel";
describe("FleetFinalDashPanel", () => { it("renders", () => {
    const { container } = render(<FleetFinalDashPanel services={1700} files={10622} lines={282500} healthPct={99.5} status="operational" />);
    expect(container.textContent).toContain("Platform Dashboard");
    expect(container.textContent).toContain("OPERATIONAL");
}); });
