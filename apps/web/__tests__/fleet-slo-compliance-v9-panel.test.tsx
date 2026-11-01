import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSloComplianceV9Panel } from "@/components/fleet-slo-compliance-v9-panel";
describe("FleetSloComplianceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSloComplianceV9Panel slos={50} attainment={99.9} />);
    expect(container.textContent).toContain("SLO Compliance v9");
}); });
