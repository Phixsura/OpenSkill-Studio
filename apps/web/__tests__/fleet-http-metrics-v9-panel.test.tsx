import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHttpMetricsV9Panel } from "@/components/fleet-http-metrics-v9-panel";
describe("FleetHttpMetricsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetHttpMetricsV9Panel endpoints={200} errorRate={0.1} />);
    expect(container.textContent).toContain("HTTP Metrics v9");
}); });
