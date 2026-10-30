import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-platform-overview-dashboard-card";

describe("PlatformOverviewDashboardCard", () => {
  it("shows overview", () => {
    const overview = { total_consumers: 100, active_24h: 85, total_requests_24h: 500000, uptime_pct: 99.95, error_rate_pct: 0.5, avg_latency_ms: 45, health: "healthy", revenue: "$12,345.67", webhook_success: 99 };
    const { container } = render(<Card overview={overview} alerts={[]} appName="OpenSkill" />);
    expect(container.textContent).toContain("Platform Overview");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("85/100");
    expect(container.textContent).toContain("$12,345.67");
  });
  it("shows alerts", () => {
    const overview = { total_consumers: 10, active_24h: 3, total_requests_24h: 100, uptime_pct: 95, error_rate_pct: 15, avg_latency_ms: 500, health: "critical", revenue: "$100.00", webhook_success: 80 };
    const { container } = render(<Card overview={overview} alerts={["🔴 2 active incidents"]} appName="App" />);
    expect(container.textContent).toContain("2 active incidents");
  });
});
