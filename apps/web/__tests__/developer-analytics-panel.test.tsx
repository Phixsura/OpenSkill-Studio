import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperAnalyticsPanel } from "@/components/developer-analytics-panel";

const mockDaily = [
  { date: "Oct 25", installs: 15, uninstalls: 2, apiCalls: 3500, revenue: 2999 },
  { date: "Oct 24", installs: 20, uninstalls: 1, apiCalls: 4200, revenue: 1999 },
];

const mockExtensions = [
  { extensionId: "e1", extensionName: "Slack Bot", totalInstalls: 500, activeInstalls: 320, totalRevenue: 15000, avgRating: 4.7 },
  { extensionId: "e2", extensionName: "Analytics", totalInstalls: 200, activeInstalls: 180, totalRevenue: 8000, avgRating: 4.3 },
];

describe("DeveloperAnalyticsPanel", () => {
  it("renders summary metrics", () => {
    const { container } = render(
      <DeveloperAnalyticsPanel dailyMetrics={mockDaily} extensions={mockExtensions} period="Last 7 days" />
    );
    expect(container.textContent).toContain("Developer Analytics");
    expect(container.textContent).toContain("Last 7 days");
    expect(container.textContent).toContain("Net Installs");
    expect(container.textContent).toContain("API Calls");
  });

  it("renders daily breakdown", () => {
    const { container } = render(
      <DeveloperAnalyticsPanel dailyMetrics={mockDaily} extensions={mockExtensions} period="Last 7 days" />
    );
    expect(container.textContent).toContain("Oct 25");
    expect(container.textContent).toContain("+15");
    expect(container.textContent).toContain("3,500");
  });

  it("renders per-extension metrics", () => {
    const { container } = render(
      <DeveloperAnalyticsPanel dailyMetrics={mockDaily} extensions={mockExtensions} period="Last 7 days" />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("320");
    expect(container.textContent).toContain("4.7");
  });
});
