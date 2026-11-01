import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPagerdutyPanel } from "@/components/fleet-pagerduty-panel";
describe("FleetPagerdutyPanel", () => { it("renders", () => {
    const { container } = render(<FleetPagerdutyPanel services={50} activeIncidents={3} acknowledged={2} avgAck={4} />);
    expect(container.textContent).toContain("PagerDuty");
    expect(container.textContent).toContain("3 active");
}); });
