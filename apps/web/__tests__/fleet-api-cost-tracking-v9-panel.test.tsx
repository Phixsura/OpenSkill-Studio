import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCostTrackingV9Panel } from "@/components/fleet-api-cost-tracking-v9-panel";
describe("FleetApiCostTrackingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCostTrackingV9Panel apis={50} cost={50000} />);
    expect(container.textContent).toContain("API Cost Tracking v9");
}); });
