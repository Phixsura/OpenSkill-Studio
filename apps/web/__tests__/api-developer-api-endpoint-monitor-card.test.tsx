import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIEndpointMonitorCard from "../src/components/api-developer-api-endpoint-monitor-card";

const monitors = [
  { method: "GET", path: "/api/users", status: "healthy", avg_response_ms: 50, error_rate_pct: 0.5, requests_per_minute: 100 },
  { method: "GET", path: "/api/search", status: "slow", avg_response_ms: 1500, error_rate_pct: 1, requests_per_minute: 10 },
];

describe("APIDeveloperAPIEndpointMonitorCard", () => {
  it("shows monitors", () => {
    const { container } = render(<APIDeveloperAPIEndpointMonitorCard monitors={monitors} appName="App" />);
    expect(container.textContent).toContain("Endpoint Monitor");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("GET /api/users");
    expect(container.textContent).toContain("50ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIEndpointMonitorCard monitors={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoints monitored");
  });
});
