import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIUsageDashboardCard from "../src/components/api-usage-dashboard-card";

const dash = { total_requests: 100000, total_errors: 500, error_rate: 0.5, unique_consumers: 50, unique_endpoints: 30, avg_latency_ms: 85, peak_rpm: 2000, quota_usage_pct: 65.0 };

describe("APIUsageDashboardCard", () => {
  it("shows all metrics", () => {
    const { container } = render(<APIUsageDashboardCard dashboard={dash} appName="App" />);
    expect(container.textContent).toContain("Usage Dashboard");
    expect(container.textContent).toContain("100,000");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("85ms");
  });
});
