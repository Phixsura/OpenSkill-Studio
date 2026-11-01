import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageAnalyticsDashboard } from "@/components/usage-analytics-dashboard";

describe("UsageAnalyticsDashboard", () => {
  const funnel = [
    { step: "Visit", count: 1000, dropOffPct: 0, conversionPct: 100 },
    { step: "Install", count: 300, dropOffPct: 70, conversionPct: 30 },
  ];
  it("renders analytics", () => {
    const { container } = render(
      <UsageAnalyticsDashboard totalEvents={5000} uniqueUsers={200} eventsPerUser={25}
        topActions={[]} funnel={funnel} overallConversion={30} />
    );
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("Visit");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("-70%");
  });
});
