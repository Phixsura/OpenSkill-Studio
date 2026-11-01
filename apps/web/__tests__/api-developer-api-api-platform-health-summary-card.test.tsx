import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPlatformHealthSummaryCard from "../src/components/api-developer-api-api-platform-health-summary-card";

const health = {
  api_uptime_pct: 99.99, avg_latency_ms: 45, error_rate_pct: 0.1,
  webhook_success_rate_pct: 99.8, webhook_queue_depth: 50,
  active_consumers: 200, total_api_calls_24h: 500000,
  security_score: 95, open_findings: 0,
  services_healthy: 10, services_total: 10, circuits_open: 0,
  overall_health: "healthy", health_score: 100,
};

describe("APIDeveloperAPIApiPlatformHealthSummaryCard", () => {
  it("shows health summary", () => {
    const { container } = render(<APIDeveloperAPIApiPlatformHealthSummaryCard health={health} appName="OpenSkill" />);
    expect(container.textContent).toContain("Platform Health");
    expect(container.textContent).toContain("HEALTHY");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("10/10");
  });
});
