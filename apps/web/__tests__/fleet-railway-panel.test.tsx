import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRailwayPanel } from "@/components/fleet-railway-panel";
describe("FleetRailwayPanel", () => { it("renders", () => {
    const { container } = render(<FleetRailwayPanel services={15} deployed={15} deploys={20} />);
    expect(container.textContent).toContain("Railway");
    expect(container.textContent).toContain("20 deploys");
}); });
