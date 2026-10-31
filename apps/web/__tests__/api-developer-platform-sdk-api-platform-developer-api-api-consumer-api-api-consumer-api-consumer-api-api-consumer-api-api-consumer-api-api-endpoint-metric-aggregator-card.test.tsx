import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-endpoint-metric-aggregator-card";

describe("EndpointMetricAggregatorCard", () => {
  it("shows metrics", () => {
    const top = [{ path: "/api/users", requests: 5000, avgMs: 75, errorRate: 0.5 }];
    const { container } = render(<Card totalRequests={10000} totalErrors={50} overallAvgMs={100} overallErrorRate={0.5} topEndpoints={top} appName="App" />);
    expect(container.textContent).toContain("Endpoint Metrics");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("100ms");
  });
  it("shows empty totals", () => {
    const { container } = render(<Card totalRequests={0} totalErrors={0} overallAvgMs={0} overallErrorRate={0} topEndpoints={[]} appName="App" />);
    expect(container.textContent).toContain("Endpoint Metrics");
  });
});
