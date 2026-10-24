import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWhAnalyticsPanel } from "@/components/fleet-wh-analytics-panel";
describe("FleetWhAnalyticsPanel", () => { it("renders", () => {
    const { container } = render(<FleetWhAnalyticsPanel totalEvents={10000} eventTypes={8} diverse={true} />);
    expect(container.textContent).toContain("Webhook Analytics");
    expect(container.textContent).toContain("Diverse event");
}); });
