import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMetricCardinalityV9Panel } from "@/components/fleet-metric-cardinality-v9-panel";
describe("FleetMetricCardinalityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMetricCardinalityV9Panel metrics={500} highCard={5} />);
    expect(container.textContent).toContain("Metric Cardinality v9");
}); });
