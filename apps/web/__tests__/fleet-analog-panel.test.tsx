import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnalogPanel } from "@/components/fleet-analog-panel";
describe("FleetAnalogPanel", () => { it("renders", () => {
    const { container } = render(<FleetAnalogPanel apps={3} deployed={3} pages={100} apiRoutes={30} />);
    expect(container.textContent).toContain("Analog");
    expect(container.textContent).toContain("30 API routes");
}); });
