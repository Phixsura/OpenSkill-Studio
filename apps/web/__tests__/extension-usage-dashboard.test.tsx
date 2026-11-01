import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionUsageDashboard } from "@/components/extension-usage-dashboard";

const mockMetrics = {
  dailyActiveUsers: 1200, weeklyActiveUsers: 3500,
  monthlyActiveUsers: 8000, totalApiCalls: 500000,
  avgSessionMinutes: 12, retentionRate: 45,
};
const mockTrends = [
  { date: "Mon", users: 1100, apiCalls: 50000 },
  { date: "Tue", users: 1200, apiCalls: 55000 },
  { date: "Wed", users: 1050, apiCalls: 48000 },
  { date: "Thu", users: 1300, apiCalls: 60000 },
  { date: "Fri", users: 1400, apiCalls: 62000 },
];

describe("ExtensionUsageDashboard", () => {
  it("renders user metrics", () => {
    const { container } = render(
      <ExtensionUsageDashboard metrics={mockMetrics} trends={mockTrends} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("3,500");
    expect(container.textContent).toContain("8,000");
  });

  it("shows DAU/WAU ratio", () => {
    const { container } = render(
      <ExtensionUsageDashboard metrics={mockMetrics} trends={mockTrends} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("34%");
  });

  it("shows retention and session", () => {
    const { container } = render(
      <ExtensionUsageDashboard metrics={mockMetrics} trends={mockTrends} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("12min");
  });

  it("renders trend bars", () => {
    const { container } = render(
      <ExtensionUsageDashboard metrics={mockMetrics} trends={mockTrends} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("Mon");
    expect(container.textContent).toContain("Fri");
  });
});
