import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPlatformStatsCard from "../src/components/api-platform-stats-card";

const stats = {
  total_services: 15, total_endpoints: 120, total_consumers: 50,
  total_api_calls: 500000, total_webhooks_sent: 100000,
  overall_health: 99.5, uptime_pct: 99.99, active_incidents: 0,
};

describe("APIPlatformStatsCard", () => {
  it("renders all metrics", () => {
    const { container } = render(<APIPlatformStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("Platform Overview");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("99.99%");
  });
});
