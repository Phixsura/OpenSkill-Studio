import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMetricCardPanel } from "@/components/fleet-metric-card-panel";
describe("FleetMetricCardPanel", () => { it("renders", () => {
    const { container } = render(<FleetMetricCardPanel totalSeries={1100000} sources={5} highCardinality={2} warning={true} />);
    expect(container.textContent).toContain("Metric Cardinality");
    expect(container.textContent).toContain("1,100,000");
}); });
