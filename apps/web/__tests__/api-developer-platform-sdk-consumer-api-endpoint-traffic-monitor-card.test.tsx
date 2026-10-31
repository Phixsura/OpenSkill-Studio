import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-traffic-monitor-card";

describe("EndpointTrafficMonitorCard", () => {
  it("shows traffic", () => {
    const summaries = [{ endpoint: "/api/users", currentRps: 75, peakRps: 120, avgRps: 60, totalRequests: 50000, alerts: [{ type: "spike", message: "RPS spike: 75" }] }];
    const { container } = render(<Card summaries={summaries} appName="App" />);
    expect(container.textContent).toContain("Traffic Monitor");
    expect(container.textContent).toContain("75 rps");
    expect(container.textContent).toContain("Peak: 120");
    expect(container.textContent).toContain("RPS spike");
  });
  it("shows empty", () => {
    const { container } = render(<Card summaries={[]} appName="App" />);
    expect(container.textContent).toContain("No traffic data");
  });
});
