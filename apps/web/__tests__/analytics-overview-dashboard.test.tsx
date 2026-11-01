import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsOverviewDashboard } from "@/components/analytics-overview-dashboard";

const data = {
  engagement: { dau: 5000, wau: 12000, mau: 30000, dauWauRatio: 41.7, avgSession: 15, retention7d: 45 },
  growth: { extensionsToday: 10, installsToday: 500, newDevsToday: 25 },
  revenue: { todayCents: 100000, projectedMonthly: 3000000 },
  api: { callsToday: 2000000 },
  satisfaction: { nps: 55 },
};

describe("AnalyticsOverviewDashboard", () => {
  it("renders analytics", () => {
    const { container } = render(<AnalyticsOverviewDashboard data={data} />);
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("41.7%");
    expect(container.textContent).toContain("$1,000");
    expect(container.textContent).toContain("2,000,000");
    expect(container.textContent).toContain("55");
  });
});
