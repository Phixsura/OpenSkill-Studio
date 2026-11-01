import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIEndpointLatencyHistogramCard from "../src/components/api-developer-api-endpoint-latency-histogram-card";

const histograms = [
  { endpoint: "/api/users", avg_ms: 45.5, p99_bucket: 500, total: 10000, buckets: { 50: 9000, 100: 900, 500: 100 } },
];

describe("APIDeveloperAPIEndpointLatencyHistogramCard", () => {
  it("shows histogram data", () => {
    const { container } = render(<APIDeveloperAPIEndpointLatencyHistogramCard histograms={histograms} appName="App" />);
    expect(container.textContent).toContain("Latency Histogram");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("avg: 45.5ms");
    expect(container.textContent).toContain("p99: 500ms");
    expect(container.textContent).toContain("10,000 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIEndpointLatencyHistogramCard histograms={[]} appName="App" />);
    expect(container.textContent).toContain("No latency data");
  });
});
