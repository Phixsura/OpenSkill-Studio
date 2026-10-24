import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHpaPanel } from "@/components/fleet-hpa-panel";
describe("FleetHpaPanel", () => { it("renders", () => {
    const { container } = render(<FleetHpaPanel total={5} atMax={1} atMin={2} scalingPressure={true} />);
    expect(container.textContent).toContain("Fleet HPA");
    expect(container.textContent).toContain("Scaling pressure");
}); });
