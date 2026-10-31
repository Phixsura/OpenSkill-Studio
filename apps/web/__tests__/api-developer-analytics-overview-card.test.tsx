import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAnalyticsOverviewCard from "../src/components/api-developer-analytics-overview-card";

const overview = { total_developers: 100, total_apps: 50, total_api_calls: 1000000, total_webhooks: 500000, avg_developer_satisfaction: 4.5, onboarding_completion_pct: 85, documentation_coverage_pct: 92, platform_health_score: 98.5 };

describe("APIDeveloperAnalyticsOverviewCard", () => {
  it("shows all metrics", () => {
    const { container } = render(<APIDeveloperAnalyticsOverviewCard overview={overview} appName="App" />);
    expect(container.textContent).toContain("Analytics Overview");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("4.5/5");
    expect(container.textContent).toContain("92%");
  });
});
