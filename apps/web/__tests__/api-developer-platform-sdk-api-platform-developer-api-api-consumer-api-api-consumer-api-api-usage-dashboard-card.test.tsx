import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-api-usage-dashboard-card";

describe("ConsumerApiUsageDashboardCard", () => {
  it("shows dashboards", () => {
    const dashboards = [{ consumer_id: "c1", requests_today: 5000, success_rate: 99.5, avg_latency_ms: 42, quota_usage_pct: 60, health_score: 95, status: "healthy", tier: "pro" }];
    const { container } = render(<Card dashboards={dashboards} degradedCount={0} appName="App" />);
    expect(container.textContent).toContain("Consumer Dashboards");
    expect(container.textContent).toContain("5,000/day");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("pro");
  });
  it("shows degraded", () => {
    const { container } = render(<Card dashboards={[]} degradedCount={3} appName="App" />);
    expect(container.textContent).toContain("3 degraded");
  });
});
