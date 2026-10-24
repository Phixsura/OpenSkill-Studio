import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiUsageAnalyticsV9Panel } from "@/components/fleet-api-usage-analytics-v9-panel";
describe("FleetApiUsageAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiUsageAnalyticsV9Panel apis={50} growing={40} />);
    expect(container.textContent).toContain("Usage Analytics v9");
}); });
