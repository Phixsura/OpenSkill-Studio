import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAdoptCurvePanel } from "@/components/fleet-adopt-curve-panel";
describe("FleetAdoptCurvePanel", () => { it("renders", () => {
    const { container } = render(<FleetAdoptCurvePanel months={6} currentUsers={500} growthPct={150} accelerating={true} />);
    expect(container.textContent).toContain("Adoption Curve");
    expect(container.textContent).toContain("Accelerating");
}); });
