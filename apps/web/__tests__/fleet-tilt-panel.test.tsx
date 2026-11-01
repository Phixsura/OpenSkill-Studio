import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTiltPanel } from "@/components/fleet-tilt-panel";
describe("FleetTiltPanel", () => { it("renders", () => {
    const { container } = render(<FleetTiltPanel total={5} running={4} resources={80} avgUpdate={1500} fast={true} />);
    expect(container.textContent).toContain("Tilt");
    expect(container.textContent).toContain("Fast updates");
}); });
