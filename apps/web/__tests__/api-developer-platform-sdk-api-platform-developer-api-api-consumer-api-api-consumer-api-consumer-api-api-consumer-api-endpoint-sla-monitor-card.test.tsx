import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-endpoint-sla-monitor-card";

describe("ConsumerApiEndpointSlaMonitorCard", () => {
  it("shows reports", () => {
    const reports = [{ path: "/api/users", inCompliance: true, availability: 99.95, latencyP99: 200, errorRate: 0.05, availOk: true, latOk: true, errOk: true }];
    const { container } = render(<Card reports={reports} appName="App" />);
    expect(container.textContent).toContain("SLA Monitor");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("99.95% avail");
    expect(container.textContent).toContain("✅");
  });
  it("shows empty", () => {
    const { container } = render(<Card reports={[]} appName="App" />);
    expect(container.textContent).toContain("No SLA targets");
  });
});
