import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsOverviewDashboard } from "@/components/analytics-overview-dashboard";

describe("AnalyticsOverviewDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <AnalyticsOverviewDashboard period="30d"
        acquisition={{ installs: 1000, uninstalls: 100, net: 900, growth_pct: 90 }}
        engagement={{ dau: 500, wau: 2000, mau: 5000, retention_30d: 72.5 }}
        performance={{ api_calls: 100000, errors: 50, error_rate: 0.05, avg_latency_ms: 45 }}
        revenue={{ total: 5000, mrr: 1500, arpu: 100 }} />
    );
    expect(container.textContent).toContain("Analytics Overview");
    expect(container.textContent).toContain("+1,000");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("72.5%");
    expect(container.textContent).toContain("$5,000");
    expect(container.textContent).toContain("$1,500");
  });
});
