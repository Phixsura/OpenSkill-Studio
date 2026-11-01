import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-latency-percentile-card";

describe("LatencyPercentileCard", () => {
  it("shows latency data", () => {
    const endpoints = [{ endpoint: "/api", method: "GET", p50: 25, p95: 100, p99: 250, avg: 50, count: 5000 }];
    const { container } = render(<Card endpoints={endpoints} slowCount={0} appName="App" />);
    expect(container.textContent).toContain("Latency Percentiles");
    expect(container.textContent).toContain("p50: 25ms");
    expect(container.textContent).toContain("p99: 250ms");
    expect(container.textContent).toContain("5,000 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} slowCount={0} appName="App" />);
    expect(container.textContent).toContain("No latency data");
  });
});
