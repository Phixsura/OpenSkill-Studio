import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRatePlanPanel } from "@/components/fleet-rate-plan-panel";
describe("FleetRatePlanPanel", () => { it("renders", () => {
    const { container } = render(<FleetRatePlanPanel total={100} tiers={3} />);
    expect(container.textContent).toContain("Rate Plans");
    expect(container.textContent).toContain("3 tiers");
}); });
