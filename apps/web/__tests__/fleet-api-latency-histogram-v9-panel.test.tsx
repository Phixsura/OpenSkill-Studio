import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiLatencyHistogramV9Panel } from "@/components/fleet-api-latency-histogram-v9-panel";
describe("FleetApiLatencyHistogramV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiLatencyHistogramV9Panel endpoints={200} p99={99} />);
    expect(container.textContent).toContain("Latency Histogram v9");
}); });
