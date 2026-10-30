import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-traffic-analytics-card";

describe("TrafficAnalyticsCard", () => {
  it("shows traffic", () => {
    const endpoints = [{ endpoint: "/api", method: "GET", rps: 15.5, error_rate: 2.1, request_count: 50000, unique_consumers: 120 }];
    const { container } = render(<Card endpoints={endpoints} totalRps={15.5} appName="App" />);
    expect(container.textContent).toContain("Traffic Analytics");
    expect(container.textContent).toContain("15.5 rps");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("120 consumers");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} totalRps={0} appName="App" />);
    expect(container.textContent).toContain("No traffic data");
  });
});
