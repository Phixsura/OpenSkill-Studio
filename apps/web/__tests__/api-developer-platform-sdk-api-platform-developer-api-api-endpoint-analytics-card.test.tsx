import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-analytics-card";

describe("EndpointAnalyticsCard", () => {
  it("shows analytics", () => {
    const endpoints = [{ endpoint: "/users", method: "GET", total_requests: 5000, error_rate: 2.5, avg_latency: 45, top_consumer: "c1" }];
    const { container } = render(<Card endpoints={endpoints} highErrorCount={0} appName="App" />);
    expect(container.textContent).toContain("Endpoint Analytics");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("5,000 reqs");
    expect(container.textContent).toContain("2.5%");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} highErrorCount={0} appName="App" />);
    expect(container.textContent).toContain("No analytics data");
  });
});
