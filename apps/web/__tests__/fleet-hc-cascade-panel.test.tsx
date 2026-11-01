import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHcCascadePanel } from "@/components/fleet-hc-cascade-panel";
describe("FleetHcCascadePanel", () => { it("renders", () => {
    const { container } = render(<FleetHcCascadePanel total={20} unhealthy={1} impacted={5} maxCascade={3} cascading={true} />);
    expect(container.textContent).toContain("Health Cascade");
    expect(container.textContent).toContain("Cascading failure");
}); });
