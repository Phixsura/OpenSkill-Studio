import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficAnalysisV9Panel } from "@/components/fleet-traffic-analysis-v9-panel";
describe("FleetTrafficAnalysisV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficAnalysisV9Panel apis={50} anomalous={0} />);
    expect(container.textContent).toContain("Traffic Analysis v9");
}); });
