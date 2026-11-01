import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFfAnalyticsPanel } from "@/components/fleet-ff-analytics-panel";
describe("FleetFfAnalyticsPanel", () => { it("renders", () => {
    const { container } = render(<FleetFfAnalyticsPanel totalFlags={20} enabled={15} totalEvals={50000} stale={3} />);
    expect(container.textContent).toContain("Flag Analytics");
    expect(container.textContent).toContain("3 stale");
}); });
