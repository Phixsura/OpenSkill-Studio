import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LiveMetricsDashboard } from "@/components/live-metrics-dashboard";

describe("LiveMetricsDashboard", () => {
  const metrics = { active_users: 142, requests_per_sec: 85.3, avg_response_ms: 38,
    error_rate_pct: 0.12, cpu_pct: 34.5, memory_pct: 62.1 };
  it("renders", () => {
    const { container } = render(
      <LiveMetricsDashboard metrics={metrics} alertsActive={0} lastUpdated="2026-10-23T12:00:00" />
    );
    expect(container.textContent).toContain("Live Metrics");
    expect(container.textContent).toContain("142");
    expect(container.textContent).toContain("85.3");
    expect(container.textContent).toContain("38ms");
    expect(container.textContent).toContain("34.5%");
  });
  it("shows alerts", () => {
    const { container } = render(
      <LiveMetricsDashboard metrics={metrics} alertsActive={2} lastUpdated="2026-10-23T12:00:00" />
    );
    expect(container.textContent).toContain("🚨 2 active alerts");
  });
});
