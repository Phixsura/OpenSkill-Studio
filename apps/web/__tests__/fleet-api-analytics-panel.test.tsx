import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAnalyticsPanel } from "@/components/fleet-api-analytics-panel";
describe("FleetApiAnalyticsPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiAnalyticsPanel totalCalls={100000} uniqueConsumers={500} avgCallsPerConsumer={200} topEndpoint="/api/v1/users" />);
    expect(container.textContent).toContain("API Analytics");
    expect(container.textContent).toContain("100,000 calls");
}); });
