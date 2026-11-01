import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAnalyticsV9Panel } from "@/components/fleet-api-analytics-v9-panel";
describe("FleetApiAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiAnalyticsV9Panel endpoints={100} calls={1000000} />);
    expect(container.textContent).toContain("API Analytics v9");
}); });
