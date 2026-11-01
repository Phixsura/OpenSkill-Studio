import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCustomMetricV9Panel } from "@/components/fleet-custom-metric-v9-panel";
describe("FleetCustomMetricV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCustomMetricV9Panel metrics={200} dpm={100000} />);
    expect(container.textContent).toContain("Custom Metrics v9");
}); });
