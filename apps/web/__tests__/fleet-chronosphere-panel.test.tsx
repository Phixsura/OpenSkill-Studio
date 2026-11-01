import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChronospherePanel } from "@/components/fleet-chronosphere-panel";
describe("FleetChronospherePanel", () => { it("renders", () => {
    const { container } = render(<FleetChronospherePanel tenants={3} activeSeries={15000000} avgSavings={35} />);
    expect(container.textContent).toContain("Chronosphere");
    expect(container.textContent).toContain("15,000,000");
}); });
