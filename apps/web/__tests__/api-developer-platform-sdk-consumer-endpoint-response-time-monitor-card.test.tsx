import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-endpoint-response-time-monitor-card";

describe("EndpointResponseTimeMonitorCard", () => {
  it("shows reports", () => {
    const reports = [{ path: "/api/users", sampleCount: 1000, p50: 45, p95: 200, p99: 800, p50Ok: true, p95Ok: true, p99Ok: true, allOk: true }];
    const { container } = render(<Card reports={reports} appName="App" />);
    expect(container.textContent).toContain("Response Time Monitor");
    expect(container.textContent).toContain("P50: 45ms");
    expect(container.textContent).toContain("P99: 800ms");
    expect(container.textContent).toContain("✅");
  });
  it("shows empty", () => {
    const { container } = render(<Card reports={[]} appName="App" />);
    expect(container.textContent).toContain("No response time data");
  });
});
