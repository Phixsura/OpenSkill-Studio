import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-health-dashboard-card";

describe("HealthDashboardCard", () => {
  it("shows dashboard", () => {
    const metrics = { total_consumers: 50, active_consumers: 45, total_requests_today: 100000, error_rate_pct: 1.5, avg_latency_ms: 42, uptime_pct: 99.95, active_incidents: 0 };
    const { container } = render(<Card metrics={metrics} overallHealth="healthy" degradedCount={0} appName="App" />);
    expect(container.textContent).toContain("Health Dashboard");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("45/50");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows critical", () => {
    const metrics = { total_consumers: 10, active_consumers: 3, total_requests_today: 500, error_rate_pct: 25, avg_latency_ms: 500, uptime_pct: 95, active_incidents: 2 };
    const { container } = render(<Card metrics={metrics} overallHealth="critical" degradedCount={5} appName="App" />);
    expect(container.textContent).toContain("critical");
  });
});
