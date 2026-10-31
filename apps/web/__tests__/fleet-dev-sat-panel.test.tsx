import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDevSatPanel } from "@/components/fleet-dev-sat-panel";
describe("FleetDevSatPanel", () => { it("renders", () => {
    const { container } = render(<FleetDevSatPanel responses={50} avgScore={4.2} happyPct={80} good={true} />);
    expect(container.textContent).toContain("Dev Satisfaction");
    expect(container.textContent).toContain("4.2/5");
}); });
