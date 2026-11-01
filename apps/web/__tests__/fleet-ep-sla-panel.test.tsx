import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEpSlaPanel } from "@/components/fleet-ep-sla-panel";
describe("FleetEpSlaPanel", () => { it("renders", () => {
    const { container } = render(<FleetEpSlaPanel total={20} meetingSla={19} violating={1} compliancePct={95} />);
    expect(container.textContent).toContain("Endpoint SLA");
    expect(container.textContent).toContain("95%");
}); });
